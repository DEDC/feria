document.addEventListener('DOMContentLoaded', () => {
    const chks = document.querySelectorAll('input[type="checkbox"]')

    chks.forEach(chk => {
        chk.addEventListener('click', (e) => {
            const parent = e.target.closest('.list-group-item')
            const textarea = parent.querySelector('textarea')
            if (e.target.checked) {
                textarea.name = e.target.value
                textarea.classList.remove('d-none')
            } else {
                textarea.name = ''
                textarea.classList.add('d-none')
            }
        });
    });
});