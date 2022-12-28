const tagSkillContainer = document.getElementById("tag-verification-tags-container-id");
var tagSkillSelectedTags = [];

function tagVerificationSetNoneToFalse(source) {
  if (!source.checked) {
    return;
  }
  checkbox = document.getElementById("tagVerificationUnselectAllId");
  checkbox.checked = false;
}

function tagVerficationCreateCheckbox(skillValue) {
  var checkbox = document.createElement('input');
  checkbox.type = 'checkbox';
  checkbox.id = skillValue;
  checkbox.name = 'tag-verification-skills';
  checkbox.value = skillValue;
  checkbox.setAttribute("onclick", "tagVerificationSetNoneToFalse(this)");

  var label = document.createElement('label')
  label.htmlFor = skillValue;
  label.className = "tag-verification-chip tag-verification-chip-clickable tag-verification-chip-hover"
  label.appendChild(document.createTextNode(skillValue));
  tagSkillContainer.appendChild(checkbox);
  tagSkillContainer.appendChild(label);
}

function tagVerificationFetchTags(url) {
  var csrf_token = document.cookie.split(";").find(c => c.startsWith("csrftoken="))?.split("=")[1];

  fetch(url, {
    method: "POST",
    body: JSON.stringify([]),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrf_token,
    }
  })
    .then(res => res.json())
    .then((data) => {
      data.forEach((skill) => tagVerficationCreateCheckbox(skill.name));
    });
}

tagVerificationFetchTags('{{ fetch_tags_url }}')

function tagVerificationVerifyTags(url) {
  var csrf_token = document.cookie.split(";").find(c => c.startsWith("csrftoken="))?.split("=")[1];
  var checkboxes = document.getElementsByName('tag-verification-skills');
  for(var i=0, n=checkboxes.length; i<n; i++) {
    if (checkboxes[i].checked) {
      tagSkillSelectedTags.push(checkboxes[i].value);
    }
  }
  fetch(url, {
    method: "POST",
    body: JSON.stringify(tagSkillSelectedTags),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrf_token,
    }
  })
    .then(res => res.json())
    .then(() => {
      document.querySelector("#tag-verification-action-id").style.display = "none";
      document.querySelector("#tag-verification-thankyou-container").style.display = "flex";
    })
    .catch(() => {
      document.querySelector("#tag-verification-action-id").style.display = "none";
      document.querySelector("#tag-verification-thankyou-container").style.display = "none";
      document.querySelector("#tag-verification-error-container").style.display = "flex";
    });
}

function tagVerificationUnselectAll(source) {
  if (!source.checked) {
    return;
  }
  checkboxes = document.getElementsByName('tag-verification-skills');
  for(var i=0, n=checkboxes.length;i<n;i++) {
    checkboxes[i].checked = false;
  }
}

function tagVerificationRetry() {
  document.querySelector("#tag-verification-action-id").style.display = "flex";
  document.querySelector("#tag-verification-thankyou-container").style.display = "none";
  document.querySelector("#tag-verification-error-container").style.display = "none";
  checkboxes = document.getElementsByName('tag-verification-skills');
  for(var i=0, n=checkboxes.length;i<n;i++) {
    var index = tagSkillSelectedTags.findIndex(checkboxes[i].value);
    checkboxes[i].checked = index == -1 ? false : true;
  }
}
