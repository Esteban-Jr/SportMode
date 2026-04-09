/* global Stripe */
/*
 * stripe_elements.js
 *
 * Mounts a Stripe Card Element, handles form submission via
 * stripe.confirmCardPayment(), and manages all visual feedback states:
 *
 *   - Real-time invalid border on the card element (Stripe CSS classes)
 *   - card-complete class on the wrapper when all fields are valid
 *   - Inline error message with smooth entrance animation
 *   - Spinner inside the pay button while processing
 *   - Full-page loading panel while Stripe confirms the payment
 *   - Card and button disabled during processing to prevent re-submission
 *   - Error scrolls into view on small screens
 *
 * Requires these globals to be set before this script loads:
 *   const stripePublicKey  (the pk_test_… or pk_live_… key)
 *   const clientSecret     (the PaymentIntent client secret from Django)
 */

(function () {
    'use strict';

    // -------------------------------------------------------------------------
    // Stripe initialisation
    // -------------------------------------------------------------------------
    const stripe   = Stripe(stripePublicKey);
    const elements = stripe.elements();

    // Style applied inside the Stripe iframe.
    // Keep colour palette in sync with Bootstrap / base.css.
    // 'complete' is intentionally left at the default (dark text) —
    // turning card number digits green looks wrong.
    const cardStyle = {
        base: {
            color: '#212529',
            fontFamily: '"Segoe UI", system-ui, -apple-system, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '15px',
            '::placeholder': { color: '#adb5bd' },
            iconColor: '#6c757d',
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545',
        },
    };

    const card = elements.create('card', { style: cardStyle });
    card.mount('#card-element');

    // -------------------------------------------------------------------------
    // DOM references
    // -------------------------------------------------------------------------
    const form          = document.getElementById('payment-form');
    const submitBtn     = document.getElementById('submit-button');
    const overlay       = document.getElementById('loading-overlay');
    const errorBox      = document.getElementById('card-errors');
    const cardWrap      = document.getElementById('card-element');

    // Capture the button's original markup so it can be restored after an error.
    const originalBtnHTML = submitBtn.innerHTML;

    // -------------------------------------------------------------------------
    // Real-time card feedback
    // -------------------------------------------------------------------------
    card.addEventListener('change', function (event) {
        if (event.error) {
            showError(event.error.message);
            cardWrap.classList.remove('card-complete');
            return;
        }

        clearError();

        // card-complete drives the green border via CSS — no text message needed.
        cardWrap.classList.toggle('card-complete', event.complete);
    });

    // -------------------------------------------------------------------------
    // Form submission
    // -------------------------------------------------------------------------
    form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        clearError();
        setLoading(true);

        const saveInfoEl = document.getElementById('id_save_info');
        const csrfToken  = form.querySelector('[name=csrfmiddlewaretoken]').value;

        // Step 1 — write bag snapshot into PaymentIntent metadata so the webhook
        // handler can reconstruct the order if the browser closes mid-redirect.
        fetch('/checkout/cache_checkout_data/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                csrfmiddlewaretoken: csrfToken,
                client_secret: clientSecret,
                save_info: saveInfoEl ? saveInfoEl.checked : false,
            }),
        })

        // Step 2 — ask Stripe to confirm the payment.
        .then(function (response) {
            if (!response.ok) {
                throw new Error('We could not prepare your payment. Please try again.');
            }
            return stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name:  field('full_name'),
                        email: field('email'),
                        phone: field('phone_number'),
                        address: {
                            line1:       field('street_address1'),
                            line2:       field('street_address2'),
                            city:        field('town_or_city'),
                            state:       field('county'),
                            postal_code: field('postcode'),
                            country:     field('country'),
                        },
                    },
                },
                shipping: {
                    name:  field('full_name'),
                    phone: field('phone_number'),
                    address: {
                        line1:       field('street_address1'),
                        line2:       field('street_address2'),
                        city:        field('town_or_city'),
                        state:       field('county'),
                        postal_code: field('postcode'),
                        country:     field('country'),
                    },
                },
            });
        })

        // Step 3 — handle Stripe's response.
        .then(function (result) {
            if (result.error) {
                showError(result.error.message);
                setLoading(false);
            } else if (result.paymentIntent.status === 'succeeded') {
                // POST the form — Django creates the Order and redirects to success.
                form.submit();
            }
        })

        // Network failure or unexpected exception.
        .catch(function (err) {
            showError(err.message || 'Something went wrong. Please refresh and try again.');
            setLoading(false);
        });
    });

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    function field(name) {
        const el = form.elements[name];
        return el ? el.value.trim() : '';
    }

    function showError(message) {
        errorBox.textContent = message;
        errorBox.classList.add('is-visible');
        // Bring the error into view on mobile without jumping the full page.
        errorBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function clearError() {
        errorBox.classList.remove('is-visible');
        // Text is cleared after the fade-out so it doesn't vanish mid-animation.
        setTimeout(function () {
            if (!errorBox.classList.contains('is-visible')) {
                errorBox.textContent = '';
            }
        }, 250);
    }

    function setLoading(on) {
        submitBtn.disabled = on;
        card.update({ disabled: on });

        if (on) {
            submitBtn.innerHTML =
                '<span class="spinner-border spinner-border-sm me-2" ' +
                'role="status" aria-hidden="true"></span>Processing…';
            overlay.classList.add('is-visible');
        } else {
            submitBtn.innerHTML = originalBtnHTML;
            overlay.classList.remove('is-visible');
        }
    }

})();
