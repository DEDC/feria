import {validateCURPService} from "../js/api/utilities.js"

document.addEventListener('DOMContentLoaded', () => {
    var event = new Event('change');
    const taxes = document.querySelectorAll('input[name="factura"]');
    const sted_taxes = document.querySelector('input[name="factura"]:checked')
    const regimen = document.querySelectorAll('input[name="regimen_fiscal"]');
    const sted_regimen = document.querySelector('input[name="regimen_fiscal"]:checked')
    const form = document.querySelector('#form-request')
    const element = document.querySelector('#exampleModal');
    const save_btn = document.querySelector('#save-form');
    const curp = document.querySelector('#id_curp_txt');
    const curpBtn = document.querySelector('#btnCURP');
    const nombre = document.querySelector('#id_nombre');
    const nombre_legal = document.querySelector('#id_nombre_replegal');
    var forms_list = document.querySelectorAll(".form-sol");

    // if (element) {
    const instance = new mdb.Modal(element)
    // }

    let eventoTecla = new KeyboardEvent("keydown", {
        key: "Enter",
        code: "Enter",
        keyCode: 13, // Código de la tecla Enter
        bubbles: true
    });


    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault()
            instance.show()
        })
    }

    if (save_btn) {
        save_btn.addEventListener('click', (e) => {
            e.preventDefault()
            form.submit()
        })
    }

    const moral_person = {
        'exclude': ['id_curp', 'id_curp_txt'],
        'fields': ['id_rfc_txt', 'id_nombre_replegal', 'id_constancia_fiscal', 'id_acta_constitutiva', 'id_poder_notarial']
    }

    const physical_person = {
        'exclude': ['id_acta_constitutiva', 'id_nombre_replegal', 'id_poder_notarial'],
        'fields': ['id_rfc_txt', 'id_curp_txt', 'id_curp', 'id_constancia_fiscal']
    }

    const general_person = {
        'exclude': ['id_rfc_txt', 'id_constancia_fiscal', 'id_acta_constitutiva', 'id_poder_notarial', 'id_nombre_replegal', 'reg1', 'reg2'],
        'fields': ['id_curp', 'id_curp_txt', 'id_identificacion']
    }

    taxes.forEach(element => {
        element.addEventListener('change', (e) => {
            if (e.target.value === 'False') {
                show_hide_fields(general_person.fields, general_person.exclude)
            } else {
                show_hide_fields(general_person.exclude, [])
            }
        })
    });

    regimen.forEach(element => {
        element.addEventListener('change', (e) => {
            if (e.target.value === 'fisica') {
                show_hide_fields(physical_person.fields, physical_person.exclude)
            } else if (e.target.value === 'moral') {
                show_hide_fields(moral_person.fields, moral_person.exclude)
            }
        })
    });

    function validarCURP(curp) {
        // Expresión regular para validar CURP
        const regexCURP = /^[A-Z]{1}[AEIOU]{1}[A-Z]{2}\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])[HM]{1}(AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE){1}[B-DF-HJ-NP-TV-Z]{3}[0-9A-Z]{1}\d{1}$/;

        return regexCURP.test(curp.toUpperCase());
    }

    curpBtn.addEventListener('click', async (e) => {
        if (validarCURP(curp.value)) {
            var data = []
            let timerInterval;
            Swal.fire({
                title: "Validando CURP...",
                html: "Esta ventana se cerrará al finalizar la búsqueda.",
                howLoaderOnConfirm: true,
                timer: 20000,
                timerProgressBar: true,
                didOpen: async () => {
                    Swal.showLoading();
                    data = await validateCURPService(curp.value);
                    console.log(data)
                    if (data.data.codigo == "00") {
                        nombre.value = `${data.data.datos.nombres} ${data.data.datos.apellido1} ${data.data.datos.apellido2}`;
                        nombre_legal.value = `${data.data.datos.nombres} ${data.data.datos.apellido1} ${data.data.datos.apellido2}`;
                        forms_list.forEach(element => {
                            element.style.display = "block";
                        });
                        nombre.focus();

                        // Forzar el blur (cuando pierde el foco)
                        setTimeout(() => nombre.blur(), 300);

                        nombre_legal.focus();

                        // Forzar el blur (cuando pierde el foco)
                        setTimeout(() => nombre_legal.blur(), 300);

                        Swal.close()

                    } else {
                        Swal.close()
                        nombre.value = "";
                        nombre_legal.value = "";
                        forms_list.forEach(element => {
                            element.style.display = "none";
                        });
                        Swal.fire({
                            title: 'Error!',
                            text: data.data.mensaje,
                            icon: 'error',
                            confirmButtonText: 'Aceptar'
                        });
                    }
                },
                willClose: () => {
                }
            }).then((result) => {
                /* Read more about handling dismissals below */
            });

        } else {
            curp.value = "";
            nombre.value = "";
            forms_list.forEach(element => {
                element.style.display = "none";
            });
            Swal.fire({
                title: 'CURP',
                text: 'El formato de la CURP no es válido',
                icon: 'error',
                confirmButtonText: 'Aceptar'
            })
        }
    })

    function show_hide_fields(fields, exclude) {
        for (const f of fields) {
            const field = document.querySelector(`#${f}`)
            field.required = true
            field.closest('[class^="col"]').classList.remove('d-none')
        }

        for (const f of exclude) {
            const field = document.querySelector(`#${f}`)
            field.required = false
            if (f === 'reg1' || f === 'reg2') {
                field.checked = false
            } else {
                field.value = ''
            }
            field.closest('[class^="col"]').classList.add('d-none')
        }
    }

    if (sted_taxes) {
        sted_taxes.dispatchEvent(event)
    }

    if (sted_regimen) {
        sted_regimen.dispatchEvent(event)
    }
})