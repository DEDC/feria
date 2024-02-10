document.addEventListener('DOMContentLoaded', () => {
    const taxes = document.querySelectorAll('input[name="factura"]');
    const regimen = document.querySelectorAll('input[name="regimen_fiscal"]');
    const form = document.querySelector('#form-request')
    const element = document.querySelector('#exampleModal');
    const save_btn = document.querySelector('#save-form');
    const instance = new mdb.Modal(element)

    form.addEventListener('submit', (e) => {
        e.preventDefault()
        instance.show()
    })

    save_btn.addEventListener('click', (e) => {
        e.preventDefault()
        form.submit()
    })

    const moral_person = {
        'exclude': ['id_curp', 'id_curp_txt'],
        'fields': ['id_rfc_txt', 'id_nombre_replegal', 'id_constancia_fiscal', 'id_acta_constitutiva']
    }

    const physical_person = {
        'exclude': ['id_acta_constitutiva', 'id_nombre_replegal'],
        'fields': ['id_rfc_txt', 'id_curp_txt', 'id_curp', 'id_constancia_fiscal']
    }

    const general_person = {
        'exclude': ['id_rfc_txt', 'id_constancia_fiscal', 'id_acta_constitutiva', 'id_nombre_replegal'],
        'fields': ['id_curp', 'id_curp_txt', 'id_identificacion']
    }

    taxes.forEach(element => {
        element.addEventListener('click', (e) => {
            if (e.target.value === 'False') {
                show_hide_fields(general_person.fields, general_person.exclude)
                regimen[0].disabled = true
                regimen[1].disabled = true
                regimen[0].required = false
                regimen[1].required = false
            }
            else {
                show_hide_fields(general_person.exclude, [])
                regimen[0].disabled = false
                regimen[1].disabled = false
                regimen[0].required = true
                regimen[1].required = true
            }
        })
    });

    regimen.forEach(element => {
        element.addEventListener('click', (e) => {
            if (e.target.value === 'fisica') {
                show_hide_fields(physical_person.fields, physical_person.exclude)
            }
            else if (e.target.value === 'moral') {
                show_hide_fields(moral_person.fields, moral_person.exclude)
            }
            else {
                show_hide_fields(general_person.fields, general_person.exclude)
            }
        })
    });

    function show_hide_fields(fields, exclude) {
        for (const f of fields) {
            const field = document.querySelector(`#${f}`)
            field.disabled = false
            field.required = true
            field.value = ''
        }

        for (const f of exclude) {
            const field = document.querySelector(`#${f}`)
            field.disabled = true
            field.required = false
            field.value = ''
        }
    }
})