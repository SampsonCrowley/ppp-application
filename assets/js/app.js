var submitButton = document.getElementById("uploadFiles");
var cancelButton = document.getElementById("cancelButton")
var form = document.getElementById("application-form")
var formData = new FormData()
var fileKeys = {}

var Dropzone = require("dropzone")

Dropzone.autoDiscover = false;

var myDropzone = new Dropzone("#cvb-dropzone", {
    url: "/applications/",
    maxFilesize: 5,
    addRemoveLinks: true,
    autoProcessQueue: false,
    parallelUploads: 10,
    acceptedFiles: ".pdf,.jpg,.jpeg,.gif,.tif,.png",
    uploadMultiple: true,
    init: function(){
        this.on("addedfile", function(file){
            console.log(file, formData)
            formData.append(file.upload.uuid, file)
            fileKeys[file.upload.uuid] = true
        })
        this.on("removedfile", function(file){
            console.log(file, formData)
            formData.delete(file.upload.uuid)
            delete fileKeys[file.upload.uuid]
        })
    }
});


function clearForm(){
    var inputs = form.querySelectorAll("input")
    var selects = form.querySelectorAll("select")

    for(var i = 0; i < inputs.length; i++){
        inputs[i].value = ""
    }

    for(var s = 0; s < selects.length; s++){
        selects[s].selectedIndex = 0
    }
}


function submitForm(){
    var submitData = new FormData()
    var f = 0
    for(var fileKey in fileKeys) {
        // submitData.append("files["+f+"]", formData.get(fileKey))
        submitData.append("files[]", formData.get(fileKey))
    }

    var inputs = form.querySelectorAll("input")
    var selects = form.querySelectorAll("select")
    var textareas = form.querySelectorAll("textarea")

    for(var t = 0; t < textareas.length; t++){
        var textarea = textareas[t]
        submitData.append(textarea.name, textarea.value)
    }

    for(var i = 0; i < inputs.length; i++){
        var input = inputs[i]
        submitData.append(input.name, input.value)
    }

    for(var s = 0; s < selects.length; s++){
        var select = selects[s]
        submitData.append(select.name, select.value)
    }

    var result = {}

    fetch("/applications/", {
        method: "POST",
        // headers: {
        //     "Content-Type": "multipart/form-data"
        // },
        body: submitData
    }).then(function(response){
        return response.json().then(function(json){
            result = json
        }).catch(function(error){
            result = {error: error, type: "json_error", success: false}
        })
    }).catch(function(error){
        result = {error: error, type: "response_error", success: false}
    }).finally(function(){
        result = result || {}
        console.log(result)
        if(result.success){
            // var parser = new DOMParser()
            // var template = parser.parseFromString(result.template, "text/html")
            // document.open()
            // document.write(template.body.innerText)
            // document.close()
            window.location.href = result.redirect || "/"
        } else {
            grecaptcha.reset()
            var formErrorEl = document.getElementById("form-errors")
            switch(result.type) {
                case "validation":
                    console.log(result.errors)
                    validationErrors(result.errors, formErrorEl)
                    break;
                case "error":
                    console.log(result.message)
                    formErrorEl.innerHTML = `<div class="list-group mt-1 mb-3">
                                                <span class="list-group-item list-group-item-danger">
                                                    ${result.message}
                                                </span>
                                            </div>`
                    break;
                // case "json_error":
                //     console.log(result.error)
                //     break;
                // case "response_error":
                //     console.log(result.error)
                //     break;
                default:
                    console.log("Unknown Error")
                    console.error(result.error)
                    unknownError(result.error, formErrorEl)

            }
            formErrorEl.scrollIntoView(true, {behavior: "smooth", block: "start", inline: "nearest"})
        }
    })
}


function unknownError(error, wrapper){
    var list = document.createElement("DIV")
    list.classList.add("list-group", "mt-1", "mb-3")
    var item = document.createElement("SPAN")
    item.classList.add("list-group-item", "list-group-item-danger")
    item.innerText = "An unexpected error occurred" + ": " + error.message
    list.appendChild(item)
    wrapper.innerHTML = ""
    wrapper.appendChild(list)
}


function validationErrors(errors, wrapper){
    var csrf_token = errors.csrf_token
    delete errors.csrf_token
    var errorCount = Object.keys(errors).length
    if(csrf_token){
        generateCSRF(!errorCount, wrapper)
    } 
    if(errorCount){
        var list = document.createElement("DIV")
        list.classList.add("list-group", "mt-1", "mb-3")
    
        for(var id in errors ){
            var input = document.getElementById(id)
            var label = input ? input.parentElement.querySelector("label") : null
            var prefix = label ? label.innerText : (id[0].toUpperCase() + id.slice(1))
            var messages = errors[id]
            for(var m = 0; m < messages.length; m++){
                var error = document.createElement("A")
                error.classList.add("list-group-item", "list-group-item-danger")
                error.href="#" + id
                error.innerText = prefix + ": " + messages[m]
                list.appendChild(error)
            }
        }
        wrapper.innerHTML = ""
        wrapper.appendChild(list)    
    }
}


function generateCSRF(submit, wrapper){
    fetch("/applications/new-csrf").then(function(response){
        return response.json().then(function(json){
            result = json
        }).catch(function(error){
            result = {error: error, type: "json_error", success: false}
        })
    }).catch(function(error){
        result = {error: error, type: "response_error", success: false}
    }).finally(function(){
        result = result || {}
        console.log(result)
        if(result.token){
            var parser = new DOMParser()
            var template = parser.parseFromString(result.token, "text/html")
            var currentTokenEl = document.getElementById("csrf_token")
            var currentTokenWrapper = currentTokenEl.parentElement
            currentTokenWrapper.removeChild(currentTokenEl)
            currentTokenWrapper.appendChild(template.body.firstChild)
            submit && submitForm()
        } else {
            var formErrorEl = document.getElementById("form-errors")
            console.log("Unknown Error")
            console.error(result.error)
            unknownError(result.error, wrapper)
        }
    })
}


form.addEventListener("click", function(ev){
    ev.preventDefault()
    var target = ev.target
    console.log(ev, target, target===submitButton)
    if(target === submitButton) submitForm()
    else if(target === cancelButton) clearForm();
});
