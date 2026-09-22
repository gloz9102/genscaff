(function () {
  'use strict';
  const state = { seat: 'standard', seatLabel: '스탠다드석', price: 2000, hours: 1 };
  const menuToggle = document.querySelector('.menu-toggle');
  const primaryNav = document.querySelector('.primary-nav');
  const header = document.querySelector('[data-header]');
  const seatOptions = Array.from(document.querySelectorAll('.seat-option'));
  const durationOptions = Array.from(document.querySelectorAll('.duration-option'));
  const totalPrice = document.querySelector('[data-total-price]');
  const summarySeat = document.querySelector('[data-summary-seat]');
  const summaryHours = document.querySelector('[data-summary-hours]');
  const backdrop = document.querySelector('[data-modal-backdrop]');
  const modal = document.querySelector('.plan-modal');
  const modalClose = document.querySelector('.modal-close');
  const modalEdit = document.querySelector('.modal-edit');
  let lastFocused;

  function formatPrice(amount) { return amount.toLocaleString('ko-KR'); }
  function updateEstimate() {
    const total = state.price * state.hours;
    summarySeat.textContent = state.seatLabel;
    summaryHours.textContent = state.hours;
    totalPrice.innerHTML = formatPrice(total) + '<small>원</small>';
  }
  function chooseSeat(option) {
    seatOptions.forEach((item) => {
      const selected = item === option;
      item.classList.toggle('is-selected', selected);
      item.setAttribute('aria-checked', String(selected));
    });
    state.seat = option.dataset.seat;
    state.seatLabel = option.dataset.label;
    state.price = Number(option.dataset.price);
    updateEstimate();
  }
  function chooseDuration(option) {
    durationOptions.forEach((item) => {
      const selected = item === option;
      item.classList.toggle('is-selected', selected);
      item.setAttribute('aria-checked', String(selected));
    });
    state.hours = Number(option.dataset.hours);
    updateEstimate();
  }
  function closeMenu() {
    primaryNav.classList.remove('is-open');
    menuToggle.setAttribute('aria-expanded', 'false');
  }
  function openModal() {
    lastFocused = document.activeElement;
    document.querySelector('[data-modal-seat]').textContent = state.seatLabel;
    document.querySelector('[data-modal-hours]').textContent = state.hours;
    document.querySelector('[data-modal-total]').textContent = formatPrice(state.price * state.hours) + '원';
    backdrop.hidden = false;
    modal.hidden = false;
    document.body.classList.add('modal-open');
    modalClose.focus();
  }
  function closeModal() {
    backdrop.hidden = true;
    modal.hidden = true;
    document.body.classList.remove('modal-open');
    if (lastFocused) lastFocused.focus();
  }

  menuToggle.addEventListener('click', function () {
    const isOpen = primaryNav.classList.toggle('is-open');
    menuToggle.setAttribute('aria-expanded', String(isOpen));
  });
  primaryNav.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  seatOptions.forEach((option) => option.addEventListener('click', () => chooseSeat(option)));
  durationOptions.forEach((option) => option.addEventListener('click', () => chooseDuration(option)));
  document.querySelector('.confirm-plan').addEventListener('click', openModal);
  modalClose.addEventListener('click', closeModal);
  backdrop.addEventListener('click', closeModal);
  modalEdit.addEventListener('click', function () {
    closeModal();
    document.querySelector('#calculator').scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    setTimeout(() => seatOptions.find((option) => option.dataset.seat === state.seat).focus(), 350);
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      if (modal && !modal.hidden) closeModal();
      else if (primaryNav.classList.contains('is-open')) closeMenu();
    }
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      const group = event.target.closest('[role="radiogroup"]');
      if (!group) return;
      const options = Array.from(group.querySelectorAll('[role="radio"]'));
      const index = options.indexOf(event.target);
      if (index < 0) return;
      const direction = event.key === 'ArrowRight' ? 1 : -1;
      const next = options[(index + direction + options.length) % options.length];
      next.focus();
      next.click();
      event.preventDefault();
    }
    if (event.key === 'Tab' && modal && !modal.hidden) {
      const focusable = Array.from(modal.querySelectorAll('button')).filter((item) => !item.disabled);
      const first = focusable[0]; const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { last.focus(); event.preventDefault(); }
      else if (!event.shiftKey && document.activeElement === last) { first.focus(); event.preventDefault(); }
    }
  });
  window.addEventListener('scroll', () => header.classList.toggle('is-scrolled', window.scrollY > 30), { passive: true });
  updateEstimate();
}());
