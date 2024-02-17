document.addEventListener('DOMContentLoaded', () => {
    var event = new Event('change');
    const taxes = document.querySelectorAll('input[name="factura"]');
    const sted_taxes = document.querySelector('input[name="factura"]:checked')
    const regimen = document.querySelectorAll('input[name="regimen_fiscal"]');
    const sted_regimen = document.querySelector('input[name="regimen_fiscal"]:checked')
    const form = document.querySelector('#form-request')
    const element = document.querySelector('#exampleModal');
    const save_btn = document.querySelector('#save-form');
    if (element) {
        const instance = new mdb.Modal(element)
    }

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
        'fields': ['id_rfc_txt', 'id_nombre_replegal', 'id_constancia_fiscal', 'id_acta_constitutiva']
    }

    const physical_person = {
        'exclude': ['id_acta_constitutiva', 'id_nombre_replegal'],
        'fields': ['id_rfc_txt', 'id_curp_txt', 'id_curp', 'id_constancia_fiscal']
    }

    const general_person = {
        'exclude': ['id_rfc_txt', 'id_constancia_fiscal', 'id_acta_constitutiva', 'id_nombre_replegal', 'reg1', 'reg2'],
        'fields': ['id_curp', 'id_curp_txt', 'id_identificacion']
    }

    taxes.forEach(element => {
        element.addEventListener('change', (e) => {
            if (e.target.value === 'False') {
                show_hide_fields(general_person.fields, general_person.exclude)
            }
            else {
                show_hide_fields(general_person.exclude, [])
            }
        })
    });

    regimen.forEach(element => {
        element.addEventListener('change', (e) => {
            if (e.target.value === 'fisica') {
                show_hide_fields(physical_person.fields, physical_person.exclude)
            }
            else if (e.target.value === 'moral') {
                show_hide_fields(moral_person.fields, moral_person.exclude)
            }
        })
    });

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
            }
            else {
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