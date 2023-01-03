const tagSkillContainer = document.getElementById("tag-verification-tags-container-id");
var tagSkillVerifiedTags = [];
var tagSkillIgnoredTags = [];

function tagVerificationSetNoneToFalse(source) {
  if (!source.checked) {
    return;
  }
  checkbox = document.getElementById("tagVerificationUnselectAllId");
  checkbox.checked = false;
}

function tagVerificationVerifyTags(url) {
  var csrf_token = document.cookie.split(";").find(c => c.startsWith("csrftoken="))?.split("=")[1];
  var checkboxes = document.getElementsByName('tag-verification-skills');
  var noneSelectedCheckbox = document.getElementById('tagVerificationUnselectAllId');
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
  if (tagSkillVerifiedTags.length === 0 && !noneSelectedCheckbox.checked) {
    alert("Please select atleast one skill or check 'None of these subjects were covered' checkbox!");
    return;
  }
  fetch(url, {
    method: "POST",
    body: JSON.stringify({
      verified_skills: tagSkillVerifiedTags,
      ignored_skills: tagSkillIgnoredTags,
    }),
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
  for (var i = 0, n = checkboxes.length; i < n; i++) {
    checkboxes[i].checked = false;
  }
}

function tagVerificationRetry() {
  document.querySelector("#tag-verification-action-id").style.display = "flex";
  document.querySelector("#tag-verification-thankyou-container").style.display = "none";
  document.querySelector("#tag-verification-error-container").style.display = "none";
}