import { getNave1Data, setPlaceTemp, unsetPlaceTemp, setPlace } from "../js/api/utilities.js";

document.addEventListener('DOMContentLoaded', () => {
    const chks = document.querySelectorAll('input[type="checkbox"]')
    const table_places = document.querySelector('.table-places')
    const reload_places = document.querySelector('#reload-places')
    const btn_preselect = document.querySelector('#preselection')
    const btn_select = document.querySelector('#selection')
    const timer = new easytimer.Timer();
    const modal_select = document.querySelector('#modal-timer');
    const instance_select_modal = new mdb.Modal(modal_select)
    const request_uuid = document.querySelector('#request-uuid')

    modal_select.addEventListener('hide.mdb.modal', () => {
        remove_temp_places()
    });

    timer.addEventListener('targetAchieved', function (e) {
        instance_select_modal.hide()
    });

    btn_select.addEventListener('click', (e) => {
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
            e.preventDefault()
            const data = new FormData();
            let places = document.querySelectorAll('td.selected')
            places.forEach(element => {
                data.append('places', element.dataset.uuid);
            });
            setPlaceTemp(request_uuid.value, data).then((resp) => {
                console.log(resp)
            }).then(() => {
                instance_select_modal.show()
                timer.start({ target: { minutes: 35 } });
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
            get_places()
        })
    }

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

    async function get_places() {
        getNave1Data().then((resp) => {
            table_places.textContent = ''
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
                    place.style.backgroundColor = p.color
                    place.textContent = p.text
                    place.dataset.uuid = p.uuid
                    place.dataset.status = p.status
                    if (p.status === 'available') {
                        place.addEventListener('click', (e) => {
                            e.target.classList.toggle('selected')
                            if (e.target.classList.contains('selected')) {
                                btn_preselect.disabled = false;
                            }
                            document.querySelectorAll('td.selected').length == 0 ? btn_preselect.disabled = true : btn_preselect.disabled = false
                        })
                    }
                }
            });
            mdb.Alert.getInstance(document.getElementById('alert-success')).show();
        }).catch((error) => {
            console.log(error);
        });
    }
    get_places()
});