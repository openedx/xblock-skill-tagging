const tagSkillContainer = document.getElementById("tag-verification-tags-container-id");
var tagSkillVerifiedTags = [];
var tagSkillIgnoredTags = [];

function tagVerificationToggleSubmitButton() {
  var enable = false;
  checkboxes = Array.from(document.getElementsByName('tag-verification-skills'));
  checkboxes.push(document.getElementById("tagVerificationUnselectAllId"));
  for (var i = 0, n = checkboxes.length; i < n; i++) {
    if (checkboxes[i].checked) {
      enable = true;
      break;
    };
  }
  var submitButton = document.getElementById("tagVerificationSubmitButton");
  submitButton.disabled = !enable;
}

function tagVerificationOnSkillClick(source) {
  tagVerificationToggleSubmitButton();
  if (!source.checked) {
    return;
  }
  checkbox = document.getElementById("tagVerificationUnselectAllId");
  checkbox.checked = false;
}

// https://www.quirksmode.org/js/cookies.html
function readCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

function tagVerificationVerifyTags(url) {
  var csrftoken = readCookie("csrftoken");
  if (!csrftoken) {
    alert("csrftoken not found! Please refresh the page or re login");
    return;
  }
  var checkboxes = document.getElementsByName('tag-verification-skills');
  // clear containers
  tagSkillVerifiedTags = [];
  tagSkillIgnoredTags = [];
  for (var i = 0, n = checkboxes.length; i < n; i++) {
    if (checkboxes[i].checked) {
      tagSkillVerifiedTags.push(parseInt(checkboxes[i].value));
    } else {
      tagSkillIgnoredTags.push(parseInt(checkboxes[i].value));
    }
  }
  fetch(url, {
    method: "POST",
    body: JSON.stringify({
      verified_skills: tagSkillVerifiedTags,
      ignored_skills: tagSkillIgnoredTags,
    }),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
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

function tagVerificationOnNoneCheckboxClick(source) {
  tagVerificationToggleSubmitButton();
  if (!source.checked) {
    return;
  }
  checkboxes = document.getElementsByName('tag-verification-skills');
  for (var i = 0, n = checkboxes.length; i < n; i++) {
    checkboxes[i].checked = false;
  }
}

function tagVerificationRetry() {
  document.querySelector("#tag-verification-action-id").style.display = "flex";
  document.querySelector("#tag-verification-thankyou-container").style.display = "none";
  document.querySelector("#tag-verification-error-container").style.display = "none";
}
