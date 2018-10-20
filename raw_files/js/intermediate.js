function setActiveStyleSheet(title) {
  var i, a, main;
  for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
    if(a.getAttribute("rel").indexOf("style") != -1 && a.getAttribute("title")) {
      a.disabled = true;
      if(a.getAttribute("title") == title) a.disabled = false;
    }
  }
}

function getActiveStyleSheet() {
  var i, a;
  for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
    if(a.getAttribute("rel").indexOf("style") != -1 && a.getAttribute("title") && !a.disabled) return a.getAttribute("title");
  }
  return null;
}

function getPreferredStyleSheet() {
  var i, a;
  for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
    if(a.getAttribute("rel").indexOf("style") != -1
       && a.getAttribute("rel").indexOf("alt") == -1
       && a.getAttribute("title")
       ) return a.getAttribute("title");
  }
  return null;
}

function createCookie(name,value,days) {
  if (days) {
    var date = new Date();
    date.setTime(date.getTime()+(days*24*60*60*1000));
    var expires = "; expires="+date.toGMTString();
  }
  else expires = "";
  document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for(var i=0;i < ca.length;i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') c = c.substring(1,c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}

window.onload = function(e) {
  var cookie = readCookie("style");
  var title = cookie ? cookie : getPreferredStyleSheet();
  setActiveStyleSheet(title);
}

window.onunload = function(e) {
  var title = getActiveStyleSheet();
  createCookie("style", title, 365);
}

var cookie = readCookie("style");
var title = cookie ? cookie : getPreferredStyleSheet();
setActiveStyleSheet(title);

function handleClick()
{
  var collapse_target = this.getAttribute('href');
  collapse_target = collapse_target.slice(1, collapse_target.length);
  var child_field = document.getElementById(collapse_target);
  if(this.textContent == '[+]') {
    this.textContent = '[−]';
    child_field.className = child_field.className.replace(/\bcollapse\b/ , '' );
  }
  else {
    this.textContent = '[+]';
    child_field.className += "collapse";
  }
  return false;
}
var collapsibles = document.getElementsByClassName('collapsible');
for(var i = 0; i < collapsibles.length; i++) {
  collapsibles[i].onclick=handleClick;
}

function replyForm(me, parent){
    var commentForm = document.getElementById('comment-form');
    document.getElementById("comment-form-parent").value = parent;
    document.getElementById("cancel-reply").removeAttribute("hidden");
    insertAfter(commentForm, me);
    var commentText = document.getElementById('comment-form-text');
    commentText.selectionStart = commentText.selectionEnd = commentText.value.length;
}

function cancelReply(){
    var commentForm = document.getElementById('comment-form');
    var commentList = document.getElementById('comment-list');
    document.getElementById("comment-form-parent").value = '';
    document.getElementById("cancel-reply").setAttribute("hidden", "");
    insertAfter(commentForm, commentList);
}

function insertAfter(newElement,targetElement) {
    //target is what you want it to go after. Look for this elements parent.
    var parent = targetElement.parentNode;

    //if the parents lastchild is the targetElement...
    if(parent.lastchild == targetElement) {
    //add the newElement after the target element.
    parent.appendChild(newElement);
    } 
    else {
    // else the target has siblings, insert the new element between the target and    it's next sibling.
     parent.insertBefore(newElement, targetElement.nextSibling);
    }
}

function insertBBCode(text) {
    var el = document.getElementById('comment-form-text');
    var val = el.value, startIndex, endIndex, range, offset, replacement;
    var tagOpen = "[" + text + "]";
    var tagClose = "[/" + text + "]";
    if (typeof el.selectionStart != "undefined" && typeof el.selectionEnd != "undefined") {
        startIndex = el.selectionStart;
        endIndex = el.selectionEnd;
        replacement = tagOpen + val.slice(startIndex, endIndex) + tagClose;
        el.value = val.slice(0, startIndex) + replacement + val.slice(endIndex);
        el.selectionStart = el.selectionEnd = endIndex + text.length;
        el.focus();
        if (startIndex == endIndex) offset = 2 + text.length;
        else offset = replacement.length;
        el.setSelectionRange(startIndex+offset, startIndex+offset);
    } else if (typeof document.selection != "undefined" && typeof document.selection.createRange != "undefined") {
        el.focus();
        range = document.selection.createRange();
        range.collapse(false);
        range.text = text;
        range.select();
    }
    return false;
}

// Navbar and dropdowns
var toggle = document.getElementsByClassName('navbar-toggle')[0],
    collapse = document.getElementsByClassName('navbar-collapse')[0],
    dropdowns = document.getElementsByClassName('dropdown');;

// Toggle if navbar menu is open or closed
function toggleMenu() {
    collapse.classList.toggle('collapse');
}

// Close all dropdown menus
function closeMenus() {
    for (var j = 0; j < dropdowns.length; j++) {
        dropdowns[j].getElementsByClassName('dropdown-toggle')[0].classList.remove('dropdown-open');
        dropdowns[j].classList.remove('open');
    }
}

// Add click handling to dropdowns
for (var i = 0; i < dropdowns.length; i++) {
    dropdowns[i].addEventListener('click', function() {
        if (document.body.clientWidth < 992) {
            var open = this.classList.contains('open');
            closeMenus();
            if (!open) {
                this.getElementsByClassName('dropdown-toggle')[0].classList.toggle('dropdown-open');
                this.classList.toggle('open');
            }
        }
    });
}

// Close dropdowns when screen becomes big enough to switch to open by hover
function closeMenusOnResize() {
    if (document.body.clientWidth < 992) {
      collapse.classList.add('collapse');
    }
    else {
      closeMenus();
      collapse.classList.remove('collapse');
    }
}

window.addEventListener('resize', closeMenusOnResize, false);
toggle.addEventListener('click', toggleMenu, false);

function handleChangeClick()
{
  document.getElementById('comment_group_name').removeAttribute('hidden');
  document.getElementById('comment_group_email').removeAttribute('hidden');
  document.getElementById('comment_group_website').removeAttribute('hidden');
  document.getElementById('comment_collapse').style.display = "none";
  return false;
}