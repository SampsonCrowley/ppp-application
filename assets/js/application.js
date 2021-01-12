const Dropzone     = require("dropzone"),
      submitButton = document.getElementById("uploadFiles"),
      cancelButton = document.getElementById("cancelButton"),
      dropZoneEl   = document.getElementById("cvb-dropzone"),
      form         = document.getElementById("application-form"),
      dropzoneData = new FormData(),
      fileKeys     = {};

Dropzone.autoDiscover = false;

if(dropZoneEl) {
  /* eslint-disable-next-line no-new */
  new Dropzone(dropZoneEl, {
    url: "/applications/",
    maxFilesize: 5,
    addRemoveLinks: true,
    autoProcessQueue: false,
    parallelUploads: 10,
    acceptedFiles: ".pdf,.jpg,.jpeg,.gif,.tif,.png",
    uploadMultiple: true,
    init: function initDropzone() {
      this.on("addedfile", (file) => {
        console.debug(file, dropzoneData);
        dropzoneData.append(file.upload.uuid, file);
        fileKeys[file.upload.uuid] = true;
      });

      this.on("removedfile", (file) => {
        console.debug(file, dropzoneData);
        dropzoneData.delete(file.upload.uuid);
        delete fileKeys[file.upload.uuid];
      });
    },
  });
}

async function sendToServer(url, data) {
  try {
    /* eslint-disable */
    const response =
      data
        ? await fetch(
                  url,
                  {
                    method: "POST",
                    body: data
                  }
                )
        : await fetch(url)
    /* eslint-enable */

    const json = await response.json();
    return json;
  } catch(error) {
    return { error, type: "response_error", success: false };
  }
}

async function generateCSRF(submit, wrapper) {
  const result = sendToServer("/applications/new-csrf");

  console.debug(result);

  if(result.token) {
    const parser = new DOMParser(),
          template = parser.parseFromString(result.token, "text/html"),
          currentTokenEl = document.getElementById("csrf_token"),
          currentTokenWrapper = currentTokenEl.parentElement;

    currentTokenWrapper.removeChild(currentTokenEl);
    currentTokenWrapper.appendChild(template.body.firstChild);

    if(submit) submitForm(); //eslint-disable-line
  } else {
    console.debug("Unknown Error: CSRF Reload");
    console.error(result.error);
    unknownError(result.error, wrapper); //eslint-disable-line
  }
}

function validationErrors(errors, wrapper) {
  const { csrf_token: csrfToken } = errors;

  delete errors.csrf_token;

  const errorCount = Object.keys(errors).length;

  if(csrfToken) generateCSRF(!errorCount, wrapper);

  if(errorCount) {
    const list = document.createElement("DIV");

    list.classList.add("list-group", "mt-1", "mb-3");

    for(const id in errors) {
      const input = document.getElementById(id),
            label = input ? input.parentElement.querySelector("label") : null,
            prefix = label ? label.innerText : (id[0].toUpperCase() + id.slice(1)),
            messages = errors[id];

      for(let m = 0; m < messages.length; m++) {
        const error = document.createElement("A");

        error.classList.add("list-group-item", "list-group-item-danger");
        error.href = `#${id}`;
        error.innerText = `${prefix}: ${messages[m]}`;

        list.appendChild(error);
      }
    }

    wrapper.innerHTML = "";
    wrapper.appendChild(list);
  }
}

function unknownError(error, wrapper) {
  const list = document.createElement("DIV"),
        item = document.createElement("SPAN");

  list.classList.add("list-group", "mt-1", "mb-3");

  item.classList.add("list-group-item", "list-group-item-danger");
  item.innerText = `An unexpected error occurred: ${error.message}`;

  list.appendChild(item);

  wrapper.innerHTML = "";
  wrapper.appendChild(list);
}

function handleError(result) {
  const formErrorEl = document.getElementById("form-errors");

  switch(result.type) {
    case "validation":
      console.debug(result.errors);
      validationErrors(result.errors, formErrorEl);
      break;
    case "error":
      console.debug(result.message);
      formErrorEl.innerHTML = `<div class="list-group mt-1 mb-3">
                                  <span class="list-group-item list-group-item-danger">
                                      ${result.message}
                                  </span>
                              </div>`;
      break;
    default:
      console.debug(`Unknown Error: ${result.type}`);
      console.error(result.error);
      unknownError(result.error, formErrorEl);
  }

  grecaptcha.reset(); //eslint-disable-line
  formErrorEl.scrollIntoView(true, { behavior: "smooth", block: "start", inline: "nearest" });
}

function clearForm(ev) {
  if(ev) ev.preventDefault();

  const inputs = form.querySelectorAll("input,textarea"),
        selects = form.querySelectorAll("select");

  for(let i = 0; i < inputs.length; i++) inputs[i].value = "";

  for(let s = 0; s < selects.length; s++) selects[s].selectedIndex = 0;
}

async function submitForm(ev) {
  if(ev) ev.preventDefault();

  const submitData = new FormData(),
        inputs = form.querySelectorAll("input,textarea"),
        selects = form.querySelectorAll("select");

  for(const k in fileKeys) submitData.append("files[]", dropzoneData.get(k));

  for(let i = 0; i < inputs.length; i++) {
    const input = inputs[i];
    submitData.append(input.name, input.value);
  }

  for(let s = 0; s < selects.length; s++) {
    const select = selects[s];
    submitData.append(select.name, select.value);
  }

  const result = await sendToServer("/applications/", submitData);

  console.debug(result);
  if(result.success) window.location.href = result.redirect || "/";
  else handleError(result);
}

form.addEventListener("click", (ev) => {
  const target = ev.target //eslint-disable-line

  console.debug(ev, target, target === submitButton);

  if(target === submitButton) submitForm(ev);
  else if(target === cancelButton) clearForm(ev);
});
