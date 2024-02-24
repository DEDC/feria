import { getPlaces, setPlaceTemp, unsetPlaceTemp, setPlace } from "../js/api/utilities.js";
import { url_nave_1, url_nave_3, url_zone_a } from '../js/api/endpoints.js'

document.addEventListener('DOMContentLoaded', () => {
    const zone_a_btn = document.querySelector('#zone-a')
    const zone_b_btn = document.querySelector('#zone-b')
    const zone_c_btn = document.querySelector('#zone-c')
    const zone_d_btn = document.querySelector('#zone-d')
    const n_1_btn = document.querySelector('#n-1')
    const n_3_btn = document.querySelector('#n-2')
    const zone_title = document.querySelector('#zone_title')
    // const limit_places = document.querySelector('input[name="limit_places"]')
    const table_places = document.querySelector('.table-places')
    const reload_places = document.querySelector('#reload-places')
    const btn_preselect = document.querySelector('#preselection')
    const btn_select = document.querySelector('#selection')
    const timer = new easytimer.Timer();
    const modal_select = document.querySelector('#modal-timer');
    const instance_select_modal = new mdb.Modal(modal_select)
    const request_uuid = document.querySelector('#request-uuid')
    const config_chks = document.querySelectorAll('.config-chk')
    const add_alcohol = document.querySelector('#add-alcohol')
    const add_terraza = document.querySelector('#add-terraza')
    const list_extras = document.querySelector('#extra-products')
    const total_price = document.querySelector('#total-price')

    if (add_alcohol) {
        add_alcohol.addEventListener('click', (e) => {
            let chks = document.querySelectorAll('.config-chk:checked')
            let total_m2 = 0
            chks.forEach(element => {
                total_m2 += parseInt(element.dataset.m2)
            });
            let alcohol_price = 0

            switch (true) {
                case total_m2 <= 50:
                    alcohol_price = 34742.40
                    break;
                case total_m2 > 50 || total_m2 <= 100:
                    alcohol_price = 69484.80
                    break
                case total_m2 > 100 || total_m2 <= 150:
                    alcohol_price = 121598.40
                    break
                case total_m2 > 150:
                    alcohol_price = 260568
                    break;
            }
            console.log(alcohol_price)
            let html_text = `<li class="list-group-item d-flex justify-content-end"><h5 class="m-0 me-5 fw-bold">Total por (${chks.length}) Licencias de Alcohol por ${total_m2}m2 por día:</h5><h5 class="m-0 ms-5">$${alcohol_price}</h5><input type="hidden" name="prices" value="${alcohol_price}"></li>`
            list_extras.insertAdjacentHTML('beforeend', html_text)
            total_price.textContent = `$${sum_prices()}`
        })
    }

    if (add_terraza) {
        add_terraza.addEventListener('click', (e) => {
            const terraza_price = 4500
            let chks = document.querySelectorAll('.config-chk:checked')
            let html_text = `<li class="list-group-item d-flex justify-content-end"><h5 class="m-0 me-5 fw-bold">Total por (1) Terraza:</h5><h5 class="m-0 ms-5">$${terraza_price}</h5><input type="hidden" name="prices" value="${terraza_price}"></li>`
            chks.forEach(element => {
                list_extras.insertAdjacentHTML('beforeend', html_text)
            });
            total_price.textContent = `$${sum_prices()}`
        })
    }

    if (config_chks) {
        config_chks.forEach(element => {
            element.addEventListener('click', (e) => {
                let chks = document.querySelectorAll('.config-chk:checked')
                if (chks.length > 0) {
                    add_alcohol.disabled = false
                    add_terraza.disabled = false
                } else {
                    add_alcohol.disabled = true
                    add_terraza.disabled = true
                }
            })
        });
    }

    let current_zone = ''
    let modal_shown = false

    if (n_1_btn) {
        n_1_btn.addEventListener('click', (e) => {
            get_places_zone(url_nave_1)
            current_zone = 'n_1'
        })
    }

    if (n_3_btn) {
        n_3_btn.addEventListener('click', (e) => {
            get_places_zone(url_nave_3)
            current_zone = 'n_3'
        })
    }

    if (zone_a_btn) {
        zone_a_btn.addEventListener('click', (e) => {
            get_places_zone(url_zone_a)
            current_zone = 'z_a'
        })
    }

    modal_select.addEventListener('hide.mdb.modal', () => {
        remove_temp_places()
    });

    timer.addEventListener('targetAchieved', function (e) {
        instance_select_modal.hide()
    });

    btn_select.addEventListener('click', (e) => {
        modal_shown = false
        e.preventDefault()
        const data = new FormData();
        let places = document.querySelectorAll('td.selected')
        places.forEach(element => {
            data.append('places', element.dataset.uuid);
        });
        setPlace(request_uuid.value, data).then((resp) => {
            console.log(resp)
        }).then(() => {
            location.reload()
        }).catch((error) => {
            console.log(error);
        });
    })

    if (btn_preselect) {
        btn_preselect.addEventListener('click', (e) => {
            modal_shown = true
            e.preventDefault()
            const data = new FormData();
            let places = document.querySelectorAll('td.selected')
            places.forEach(element => {
                data.append('places', element.dataset.uuid);
            });
            setPlaceTemp(request_uuid.value, data, current_zone).then((resp) => {
                if (resp.data.status_code == 'saved') {
                    instance_select_modal.show()
                    timer.start({ countdown: true, startValues: { minutes: 30 } });
                }
                else {
                    mdb.Alert.getInstance(document.getElementById('alert-notplaces')).show();
                }
            }).catch((error) => {
                console.log(error);
            });
        });
    }

    timer.addEventListener('secondsUpdated', function (e) {
        document.querySelector('#timer').textContent = timer.getTimeValues().toString();
    });

    if (reload_places) {
        reload_places.addEventListener('click', () => {
            getPlaces()
        })
    }

    async function remove_temp_places() {
        const data = new FormData();
        let places = document.querySelectorAll('td.selected')
        places.forEach(element => {
            data.append('places', element.dataset.uuid);
        });
        unsetPlaceTemp(request_uuid.value, data).then((resp) => {
            console.log(resp)
        }).then(() => {
            mdb.Alert.getInstance(document.getElementById('alert-warning')).show();
            places.forEach(element => {
                element.classList.remove('selected')
            });
            btn_preselect.disabled = true
            timer.stop()
        }).catch((error) => {
            console.log(error);
        });
    }

    async function get_places_zone(url) {
        btn_preselect.disabled = true
        getPlaces(url).then((resp) => {
            table_places.textContent = '';
            zone_title.textContent = resp.data.title;
            for (let row = 0; row < resp.data.rows; row++) {
                let tr = document.createElement('tr');
                for (let column = 0; column < resp.data.columns; column++) {
                    let td = document.createElement('td');
                    td.dataset.coords = `${row + 1}:${column + 1}`
                    tr.appendChild(td)
                }
                table_places.appendChild(tr)
            }
            return resp.data.places
        }).then((places) => {
            places.forEach(p => {
                let place = table_places.querySelector(`td[data-coords="${p.coords}"]`)
                if (place) {
                    place.style.backgroundColor = '#14A44D'
                    place.textContent = p.text
                    place.dataset.uuid = p.uuid
                    place.dataset.status = p.status
                    if (p.status === 'available') {
                        place.addEventListener('click', (e) => {
                            e.target.classList.toggle('selected')
                            let all_selected = document.querySelectorAll('.table-places td.selected')
                            // if (all_selected.length > limit_places.value) {
                                // e.target.classList.remove('selected')
                                // all_selected = document.querySelectorAll('.table-places td.selected')
                            // }
                            all_selected.length == 0 ? btn_preselect.disabled = true : btn_preselect.disabled = false
                        })
                    }
                }
            });
            mdb.Alert.getInstance(document.getElementById('alert-success')).show();
        }).catch((error) => {
            console.log(error);
        });
    }

    window.addEventListener('beforeunload', function (e) {
        if (modal_shown) {
            remove_temp_places()
        }
    });

    function sum_prices() {
        const prices = document.querySelectorAll('input[name="prices"]')
        let sum = 0
        prices.forEach(element => {
            sum += parseInt(element.value)
        });
        return sum
    }
});