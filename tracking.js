/* Sequoia Lodges — first-party attribution capture + lead form handling.
 *
 * What this does:
 *  1. On every page load, captures ad click IDs (gclid, gbraid, wbraid, msclkid,
 *     fbclid) and UTM/ValueTrack params from the URL into localStorage.
 *     First-touch context (landing page, referrer, timestamp) is stored once;
 *     click IDs and campaign params are refreshed whenever a new ad click arrives.
 *  2. Enhances any <form data-lead-form> to submit to Formspree via fetch.
 *     Conversion events fire ONLY after Formspree returns 200 — never on
 *     button click. Stored attribution is injected as hidden fields so every
 *     lead email carries its click ID and campaign context.
 *
 * Google Ads: after creating conversion actions, fill in SL_TRACKING below
 * (see GOOGLE_ADS_SETUP.md, step 4). Leave blank until then — everything else
 * works without it.
 */
window.SL_TRACKING = window.SL_TRACKING || {
    adsId: 'AW-18320974361',
    inquiryLabel: '', // conversion label for "Accepted ADU inquiry" (primary)
    magnetLabel: ''   // conversion label for "Planning kit download" (secondary)
};

(function () {
    'use strict';

    var CLICK_IDS = ['gclid', 'gbraid', 'wbraid', 'msclkid', 'fbclid'];
    var CAMPAIGN_PARAMS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term',
        'utm_content', 'campaign_id', 'ad_group_id', 'creative_id', 'keyword',
        'matchtype', 'device'];
    var FIRST_KEY = 'sl_first_touch';
    var CLICK_KEY = 'sl_click_data';

    function gtagSafe() {
        if (typeof window.gtag === 'function') { window.gtag.apply(null, arguments); }
    }

    /* Reject anything that isn't a plausible URL-param value before storing or
     * echoing it into form fields. */
    function clean(value) {
        if (typeof value !== 'string') { return ''; }
        value = value.trim().slice(0, 200);
        return /^[A-Za-z0-9 _\-.~%+:/|{}()]*$/.test(value) ? value : '';
    }

    function readStore(key) {
        try { return JSON.parse(localStorage.getItem(key) || 'null'); }
        catch (e) { return null; }
    }
    function writeStore(key, obj) {
        try { localStorage.setItem(key, JSON.stringify(obj)); } catch (e) { /* private mode */ }
    }

    /* ---- 1. Capture ---- */
    var params = new URLSearchParams(window.location.search);

    if (!readStore(FIRST_KEY)) {
        writeStore(FIRST_KEY, {
            landing_page: clean(window.location.pathname),
            initial_referrer: clean(document.referrer.slice(0, 200)),
            first_touch_at: new Date().toISOString()
        });
    }

    var incoming = {};
    var hasNewClick = false;
    CLICK_IDS.concat(CAMPAIGN_PARAMS).forEach(function (name) {
        var v = clean(params.get(name) || '');
        if (v) {
            incoming[name] = v;
            if (CLICK_IDS.indexOf(name) !== -1 || name.indexOf('utm_') === 0) { hasNewClick = true; }
        }
    });
    if (hasNewClick) {
        /* A fresh ad/campaign click replaces prior campaign context wholesale so a
         * later Google click never inherits a stale fbclid, and vice versa. */
        incoming.click_captured_at = new Date().toISOString();
        writeStore(CLICK_KEY, incoming);
    }

    /* Google Ads site tag, once IDs are configured */
    if (window.SL_TRACKING.adsId) { gtagSafe('config', window.SL_TRACKING.adsId); }

    /* ---- 2. Lead forms ---- */
    function attributionFields() {
        var data = {};
        var first = readStore(FIRST_KEY) || {};
        var click = readStore(CLICK_KEY) || {};
        CLICK_IDS.concat(CAMPAIGN_PARAMS).forEach(function (name) {
            if (click[name]) { data[name] = click[name]; }
        });
        ['landing_page', 'initial_referrer', 'first_touch_at'].forEach(function (name) {
            if (first[name]) { data[name] = first[name]; }
        });
        data.page_url = clean(window.location.pathname);
        return data;
    }

    function setHidden(form, name, value) {
        var input = form.querySelector('input[type="hidden"][name="' + name + '"]');
        if (!input) {
            input = document.createElement('input');
            input.type = 'hidden';
            input.name = name;
            form.appendChild(input);
        }
        input.value = value;
    }

    function uuid() {
        if (window.crypto && crypto.randomUUID) { return crypto.randomUUID(); }
        return 'sl-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
    }

    function fireConversion(label, eventId, callback) {
        var cfg = window.SL_TRACKING;
        if (cfg.adsId && label) {
            gtagSafe('event', 'conversion', {
                send_to: cfg.adsId + '/' + label,
                transaction_id: eventId,
                event_callback: callback
            });
            /* Never leave the visitor hanging if the tag is blocked. */
            setTimeout(callback, 900);
        } else {
            callback();
        }
    }

    function handleForm(form) {
        var kind = form.getAttribute('data-lead-form') || 'inquiry'; /* inquiry | magnet */
        var variant = form.getAttribute('data-variant') || 'unknown';
        var thanks = form.getAttribute('data-thanks') || '/thank-you.html';
        var started = false;

        form.addEventListener('input', function () {
            if (started) { return; }
            started = true;
            gtagSafe('event', 'form_start', { form_variant: variant, form_kind: kind });
        });

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            var button = form.querySelector('button[type="submit"]');
            var errorBox = form.querySelector('[data-form-error]');
            if (errorBox) { errorBox.classList.add('hidden'); }
            if (button && button.disabled) { return; } /* double-submit guard */

            /* Honeypot: pretend success, send nothing. */
            var trap = form.querySelector('input[name="_gotcha"]');
            if (trap && trap.value) { window.location.href = thanks; return; }

            var eventId = uuid();
            var attrs = attributionFields();
            Object.keys(attrs).forEach(function (name) { setHidden(form, name, attrs[name]); });
            setHidden(form, 'event_id', eventId);
            setHidden(form, 'landing_page_variant', variant);

            var originalText;
            if (button) {
                originalText = button.textContent;
                button.disabled = true;
                button.textContent = 'Sending…';
            }

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: { 'Accept': 'application/json' }
            }).then(function (res) {
                if (!res.ok) { throw new Error('formspree_' + res.status); }

                var aduField = form.querySelector('[name="adu_type"]');
                var timelineField = form.querySelector('[name="timeline"]');
                window.dataLayer = window.dataLayer || [];
                window.dataLayer.push({
                    event: kind === 'magnet' ? 'lead_magnet_accepted' : 'lead_accepted',
                    event_id: eventId,
                    lead_type: kind === 'magnet' ? 'planning_kit' : 'adu_plan_inquiry',
                    adu_type: aduField ? clean(aduField.value) : undefined,
                    timeline_bucket: timelineField ? clean(timelineField.value) : undefined,
                    landing_page_variant: variant
                });
                gtagSafe('event', kind === 'magnet' ? 'sample_kit_download' : 'generate_lead', {
                    event_id: eventId,
                    landing_page_variant: variant
                });

                var label = kind === 'magnet'
                    ? window.SL_TRACKING.magnetLabel
                    : window.SL_TRACKING.inquiryLabel;
                var redirected = false;
                fireConversion(label, eventId, function () {
                    if (redirected) { return; }
                    redirected = true;
                    window.location.href = thanks;
                });
            }).catch(function () {
                gtagSafe('event', 'form_error', { form_variant: variant, form_kind: kind });
                if (button) { button.disabled = false; button.textContent = originalText; }
                if (errorBox) { errorBox.classList.remove('hidden'); }
            });
        });
    }

    function init() {
        Array.prototype.forEach.call(document.querySelectorAll('form[data-lead-form]'), handleForm);

        /* Secondary diagnostic events: email clicks and direct sample-plan downloads. */
        document.addEventListener('click', function (e) {
            var link = e.target && e.target.closest ? e.target.closest('a') : null;
            if (!link) { return; }
            var href = link.getAttribute('href') || '';
            if (href.indexOf('mailto:') === 0) {
                gtagSafe('event', 'email_click', { page: clean(window.location.pathname) });
            } else if (/Sequoia_Lodges_ADU_Sample_Plan\.pdf/i.test(href)) {
                gtagSafe('event', 'sample_plan_download', { page: clean(window.location.pathname) });
            }
        });
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
