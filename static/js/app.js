import {
    getAvailableDates, getAvailableTimes
} from "../js/api/utilities.js";

document.addEventListener('DOMContentLoaded', () => {
    const dates_list = document.querySelector('#dates-list');
    const times_list = document.querySelector('#times-list');
    const placeholder_dates = document.querySelector('#placeholder-dates');
    const placeholder_times = document.querySelector('#placeholder-times');
    const inp_date = document.querySelector('input[name="date"]');
    const inp_time = document.querySelector('input[name="time"]');
    const btn_save = document.querySelector('#save-date');
    const form = document.querySelector('form');

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        if (/(\d{4})-(\d{2})-(\d{2})/.test(inp_date.value) && /^(?:[01][0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?$/.test(inp_time.value)) {
            btn_save.classList.add('disabled');
            form.submit();
        }
    });

    getAvailableDates().then((resp) => {
        resp.data.forEach(element => {
            let item = `<button type="button" data-date="${element.short_format}" class="list-group-item list-group-item-action px-3 border-0">${element.text_format}</button>`;
            dates_list.insertAdjacentHTML('beforeend', item);
            dates_list.lastElementChild.addEventListener('click', (e) => {
                remove_active(dates_list)
                e.target.classList.add('active')
                inp_date.value = e.target.dataset.date;
                inp_time.value = null;
                btn_save.classList.add('disabled')
                placeholder_times.classList.remove('d-none')
                times_list.classList.add('d-none');
                clean_items(times_list);
                getAvailableTimes(e.target.dataset.date).then((resp) => {
                    resp.data.forEach(element => {
                        let item = `<button type="button" data-time="${element.short_format}" class="list-group-item list-group-item-action px-3 border-0">${element.short_format} horas</button>`;
                        times_list.insertAdjacentHTML('beforeend', item);
                        times_list.lastElementChild.addEventListener('click', (e) => {
                            remove_active(times_list)
                            e.target.classList.add('active')
                            inp_time.value = e.target.dataset.time;
                            if (inp_date && inp_time) {
                                btn_save.classList.remove('disabled')
                            }
                        })
                    });
                }).then(() => {
                    placeholder_times.classList.add('d-none')
                    times_list.classList.remove('d-none');
                }).catch((error) => {
                    console.log(error);
                });
            });
            placeholder_dates.classList.add('d-none')
            dates_list.classList.remove('d-none');
        });

    }).catch((error) => {
        console.log(error);
    })

    function remove_active(list) {
        let items = list.querySelectorAll('.active');
        items.forEach(element => {
            element.classList.remove('active')
        });
    }

    function clean_items(list) {
        list.replaceChildren();
    }
})