(() => {
  const seatPrices = { standard: 2000, wide: 2500, duo: 5000 };
  const seatNames = { standard: '스탠다드석', wide: '와이드석', duo: '듀오석' };
  const seatNotes = { standard: '개인 플레이용', wide: '넓은 책상', duo: '2인 나란히' };
  const form = document.querySelector('#plan-form');
  const totalPrice = document.querySelector('#total-price');
  const totalDetail = document.querySelector('#total-detail');
  const confirmation = document.querySelector('#plan-confirmation');
  const confirmedPlan = document.querySelector('#confirmed-plan');
  const confirmedPrice = document.querySelector('#confirmed-price');
  const editPlan = document.querySelector('#edit-plan');
  const menuToggle = document.querySelector('.menu-toggle');
  const primaryNav = document.querySelector('#primary-nav');
  const numberFormat = new Intl.NumberFormat('ko-KR');

  function getState() {
    const seat = form.querySelector('input[name="seat"]:checked').value;
    const duration = Number(form.querySelector('input[name="duration"]:checked').value);
    return { seat, duration, total: seatPrices[seat] * duration };
  }

  function updateChoiceStyles() {
    form.querySelectorAll('.seat-choice').forEach((choice) => choice.classList.toggle('is-selected', choice.querySelector('input').checked));
    form.querySelectorAll('.time-choice').forEach((choice) => choice.classList.toggle('is-selected', choice.querySelector('input').checked));
  }

  function updateTotal() {
    const { seat, duration, total } = getState();
    totalPrice.textContent = `${numberFormat.format(total)}원`;
    totalDetail.textContent = `${seatNames[seat]} · ${duration}시간`;
    updateChoiceStyles();
  }

  function closeMenu() {
    primaryNav.classList.remove('is-open');
    menuToggle.setAttribute('aria-expanded', 'false');
    primaryNav.setAttribute('aria-hidden', window.innerWidth <= 680 ? 'true' : 'false');
    menuToggle.querySelector('.sr-only').textContent = '메뉴 열기';
  }

  form.addEventListener('change', updateTotal);
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const { seat, duration, total } = getState();
    confirmedPlan.textContent = `${seatNames[seat]} · ${duration}시간`;
    confirmedPrice.textContent = `${numberFormat.format(total)}원`;
    confirmation.hidden = false;
    confirmation.focus();
  });

  editPlan.addEventListener('click', () => {
    confirmation.hidden = true;
    const firstChoice = form.querySelector('input[name="seat"]');
    firstChoice.focus();
  });

  menuToggle.addEventListener('click', () => {
    const isOpen = menuToggle.getAttribute('aria-expanded') === 'true';
    menuToggle.setAttribute('aria-expanded', String(!isOpen));
    primaryNav.classList.toggle('is-open', !isOpen);
    primaryNav.setAttribute('aria-hidden', String(isOpen));
    menuToggle.querySelector('.sr-only').textContent = isOpen ? '메뉴 열기' : '메뉴 닫기';
  });

  primaryNav.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  document.addEventListener('click', (event) => {
    if (primaryNav.classList.contains('is-open') && !primaryNav.contains(event.target) && !menuToggle.contains(event.target)) closeMenu();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && primaryNav.classList.contains('is-open')) {
      closeMenu();
      menuToggle.focus();
    }
  });
  window.addEventListener('resize', () => {
    if (window.innerWidth > 680) closeMenu();
    else primaryNav.setAttribute('aria-hidden', menuToggle.getAttribute('aria-expanded') === 'true' ? 'false' : 'true');
  });
  primaryNav.setAttribute('aria-hidden', window.innerWidth <= 680 ? 'true' : 'false');
  updateTotal();
})();
