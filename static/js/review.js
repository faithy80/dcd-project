$(document).ready(function () {
    // initialization
    const max_review = 250,
        review = document.getElementById('review'),
        review_counter = document.getElementById('review-counter');

    review_counter.textContent = `${max_review - review.value.length} characters left`;

    // review keypress event handler
    review.addEventListener('input', function () {
        review_counter.textContent = `${max_review - review.value.length} characters left`;
    });
});