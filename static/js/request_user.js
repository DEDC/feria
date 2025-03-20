import {
    getPlaces,
    setPlaceTemp,
    unsetPlaceTemp,
    setPlace,
    addTerraza,
    addAlcohol,
    addBigTerraza,
    deleteItem,
    deletePlace,
    tpayPlace, statusPlace, consultaTpayPlace,
} from "../js/api/utilities.js";
import { url_nave_1, url_nave_2, url_nave_3, url_zona_a, url_zona_b, url_zona_c, url_zona_d, url_sabor_tabasco, url_teatro } from '../js/api/endpoints.js'

document.addEventListener('DOMContentLoaded', () => {
    const n_1_btn = document.querySelector('#n-1')
    const n_2_btn = document.querySelector('#n-2')
    const n_3_btn = document.querySelector('#n-3')
    const z_a_btn = document.querySelector('#z-a')
    const z_b_btn = document.querySelector('#z-b')
    const z_c_btn = document.querySelector('#z-c')
    const z_d_btn = document.querySelector('#z-d')
    const z_sabor_btn = document.querySelector('#s-t')
    const z_teatro_btn = document.querySelector('#teatro')
    const zone_title = document.querySelector('#zone_title')
    const table_places = document.querySelector('.table-places')
    const type_pago = document.querySelector('.type_pago')
    const reload_places = document.querySelector('#reload-places')
    const btn_preselect = document.querySelector('#preselection')
    const btn_select = document.querySelector('#selection')
    const timer = new easytimer.Timer();
    const request_uuid = document.querySelector('#request-uuid')
    const config_chks = document.querySelectorAll('.config-chk')
    const add_alcohol = document.querySelector('#add-alcohol')
    const add_terraza = document.querySelector('#add-terraza')
    const add_big_terraza = document.querySelector('#add-big-terraza')
    const delete_pdt = document.querySelectorAll('.del-pdt')
    const delete_place = document.querySelectorAll('.del-place')

    const tpay_place = document.querySelectorAll('.tpay-place')
    const pdf_place = document.querySelectorAll('.pdf-place')

    tpay_place.forEach(element => {
        element.addEventListener('click', (e) => {
            tpayPlace(element.dataset.uuid).then((resp) => {
                console.log(resp);
                if(resp.data.pagado){
                    console.log("Resp", resp.pagado);
                    Swal.fire({
                      title: "Pago Realizado!",
                      text: "El pago fue procesado con existo.",
                      icon: "success"
                    }).then((result) => {
                       location.reload();
                    });
                }
                else if(resp.data.proceso){
                    console.log("Resp", resp.pagado);
                    Swal.fire({
                      title: "Estatus del pago!",
                      text: "El pago se encuentra en procesado de validacion, espere un momento.",
                      icon: "warning"
                    });
                }
                else{
                    let contentTPay = document.getElementById("content-tpay");
                    contentTPay.html = "";
                    contentTPay.appendChild(createTPay(resp.data))
                }

            }).catch((error) => {
                console.log(error);
                Swal.fire({
                  title: "Estatus del pago",
                  text: "El pago se encuentra en procesado de validacion, espere un momento.",
                  icon: "warning"
                });
            });
        })
    });

    pdf_place.forEach(element => {
        element.addEventListener('click', (e) => {
            let reciboTPay = document.getElementById("iframe");

            var title = "Mi recibo";           // Título de la ventana popup (puede ser cualquier cadena)
            var settings = "width=600,height=400,scrollbars=yes,resizable=yes";
            if(element.dataset.url != "None"){
                  // Abre el popup
                  window.open(element.dataset.url, title, settings);
            }else{
                consultaTpayPlace(element.dataset.uuid).then((resp) => {
                    console.log(resp)
                    window.open(resp.data.url_recibo, title, settings);
                }).catch((error) => {
                    console.log(error);
                });
            }

            const modal_select = document.querySelector('#modal-iframe');
            const instance_select_modal = new mdb.Modal(modal_select);
            // instance_select_modal.show()
        })
    });

    delete_pdt.forEach(element => {
        element.addEventListener('click', (e) => {
            const data = new FormData();
            data.append('item', element.dataset.uuid);
            deleteItem(request_uuid.value, element.dataset.uuid, data).then((resp) => {
                location.reload()
            }).catch((error) => {
                console.log(error);
            });
        })
    });

    delete_place.forEach(element => {
        element.addEventListener('click', (e) => {
            const data = new FormData();
            data.append('place', element.dataset.uuid);
            deletePlace(request_uuid.value, element.dataset.uuid, data).then((resp) => {
                console.log(resp);
                if(resp.data.eliminado === true){
                    location.reload()
                }else{
                    Swal.fire({
                      title: "Información del pago!",
                      text: "El lugar cuenta con un proceso de pago no puede ser eliminado.",
                      icon: "error"
                    });
                }
            }).catch((error) => {
                console.log(error);
            });
        })
    });

    if (add_alcohol) {
        add_alcohol.addEventListener('click', (e) => {
            let chks = document.querySelectorAll('.config-chk:checked')
            const data = new FormData();
            chks.forEach(element => {
                data.append('alcohol', element.value);
            });
            addAlcohol(request_uuid.value, data.get('alcohol'), data).then((resp) => {
                if(resp.data.proceso === true){
                    location.reload()
                }else{
                    Swal.fire({
                      title: "Permiso de alcohol",
                      text: "Por el momento a uno o mas lugares no se le puede agregar un permiso para venta de alcohol",
                      icon: "error"
                    });
                }
            }).catch((error) => {
                console.log(error);
            });
        })
    }

    if (add_terraza) {
        add_terraza.addEventListener('click', (e) => {
            let chks = document.querySelectorAll('.config-chk:checked')
            chks.forEach(element => {
                const data = new FormData();
                data.append('terraza', element.value);
                addTerraza(request_uuid.value, element.value, data).then((resp) => {
                    location.reload()
                }).catch((error) => {
                    console.log(error);
                });
            });
        })
    }

    if (add_big_terraza) {
        add_big_terraza.addEventListener('click', (e) => {
            let chks = document.querySelectorAll('.config-chk:checked')
            chks.forEach(element => {
                const data = new FormData();
                data.append('terraza_grande', element.value);
                addBigTerraza(request_uuid.value, element.value, data).then((resp) => {
                    location.reload()
                }).catch((error) => {
                    console.log(error);
                });
            });
        })
    }

    if (config_chks) {
        config_chks.forEach(element => {
            element.addEventListener('click', (e) => {
                let chks = document.querySelectorAll('.config-chk:checked')
                if (chks.length > 0) {
                    add_alcohol.disabled = false
                    add_terraza.disabled = false
                    add_big_terraza.disabled = false
                } else {
                    add_alcohol.disabled = true
                    add_terraza.disabled = true
                    add_big_terraza.disabled = true
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

    if (n_2_btn) {
        n_2_btn.addEventListener('click', (e) => {
            get_places_zone(url_nave_2)
            current_zone = 'n_2'
        })
    }

    if (n_3_btn) {
        n_3_btn.addEventListener('click', (e) => {
            get_places_zone(url_nave_3)
            current_zone = 'n_3'
        })
    }

    if (z_a_btn) {
        z_a_btn.addEventListener('click', (e) => {
            get_places_zone(url_zona_a)
            current_zone = 'z_a'
        })
    }

    if (z_b_btn) {
        z_b_btn.addEventListener('click', (e) => {
            get_places_zone(url_zona_b)
            current_zone = 'z_b'
        })
    }

    if (z_c_btn) {
        z_c_btn.addEventListener('click', (e) => {
            get_places_zone(url_zona_c)
            current_zone = 'z_c'
        })
    }

    if (z_d_btn) {
        z_d_btn.addEventListener('click', (e) => {
            get_places_zone(url_zona_d)
            current_zone = 'z_d'
        })
    }

    if (z_sabor_btn) {
        z_sabor_btn.addEventListener('click', (e) => {
            get_places_zone(url_sabor_tabasco)
            current_zone = 's_t'
        })
    }

    if (z_teatro_btn) {
        z_teatro_btn.addEventListener('click', (e) => {
            get_places_zone(url_teatro)
            current_zone = 'teatro'
        })
    }

    // modal_select.addEventListener('hide.mdb.modal', () => {
    //     remove_temp_places()
    // });

    timer.addEventListener('targetAchieved', function (e) {
        instance_select_modal.hide()
    });

    // btn_select.addEventListener('click', (e) => {
    //     modal_shown = false
    //     e.preventDefault()
    //     const data = new FormData();
    //     let places = document.querySelectorAll('td.selected')
    //     places.forEach(element => {
    //         data.append('places', element.dataset.uuid);
    //     });
    //     setPlace(request_uuid.value, data).then((resp) => {
    //         console.log(resp)
    //     }).then(() => {
    //         location.reload()
    //     }).catch((error) => {
    //         console.log(error);
    //     });
    // })


    if (btn_preselect) {
        btn_preselect.addEventListener('click', (e) => {            
            modal_shown = true
            e.preventDefault()
            const data = new FormData();
            let places = document.querySelectorAll('td.selected')
            if (places.length <= 3 ){
                places.forEach(element => {
                    data.append('places', element.dataset.uuid);
                });
                setPlaceTemp(request_uuid.value, data, current_zone).then((resp) => {
                    console.log(resp);
                    if (resp.data.status_code == 'saved') {
                        //instance_select_modal.show()
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
                    }
                    else {
                        //mdb.Alert.getInstance(document.getElementById('alert-notplaces')).show();
                    }
                }).catch((error) => {
                    console.log(error);
                });
            } else {
                Swal.fire({
                    title: "Selección de Lugares",
                    text: "Solo puede seleccionar como máximo 3 lugares",
                    icon: "warning"
                });
            }
        });
    }

    timer.addEventListener('secondsUpdated', function (e) {
        //document.querySelector('#timer').textContent = timer.getTimeValues().toString();
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
            // mdb.Alert.getInstance(document.getElementById('alert-warning')).show();
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
        // console.log(url);
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
});