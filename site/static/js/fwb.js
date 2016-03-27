//
// Site functionality
//

function toggleEdit(n) {
    var type = document.getElementById('edit-' + n);
    var row = document.getElementById(n);
    var children = row.childNodes;
    if (type.innerHTML == 'Edit') {
	children[0].innerHTML = '<input type="text" class="form-control" value="' + children[0].innerHTML + '">'
	children[1].innerHTML = '<input type="text" class="form-control" value="' + children[1].innerHTML + '">'
	children[2].innerHTML = '<input type="number" min="1" max="100" step="1" value="' + children[2].innerHTML + '" class="form-control">'
	children[4].innerHTML = '<button class="btn btn-success" id="edit-' + n + '" onclick="toggleEdit(' + n + ');">Save</button>'
    }
    else { // save values and reset HTML
	var newName = children[0].childNodes[0].value;
	var newDesc = children[1].childNodes[0].value;
	var newPoints = children[2].childNodes[0].value;
	$.ajax({url:"updateOffer", type:"POST", data:{name:newName,desc:newDesc,points:newPoints,offer_id:n}, success: function(r) { children[0].innerHTML = newName; children[1].innerHTML = newDesc; children[2].innerHTML = newPoints; children[4].innerHTML = '<button class="btn btn-warning" id="edit-' + n + '" onclick="toggleEdit(' + n + ');">Edit</button>'; }});
    }
}
function createOffer(group_id) {
    var form = document.getElementById("group-" + group_id);
    var elements = form.childNodes;
    var newName = elements[5].value;
    var newPoints = elements[9].value;
    var newDesc = elements[11].value;
    $.ajax({url:"createOffer", type:"POST", data:{name:newName,desc:newDesc,points:newPoints,group:group_id}, success: function(r) {
	var o = $("#tbody-" + group_id);
	o.append('<tr id="' + r + '"><td>' + newName + '</td><td>' + newDesc + '</td><td>' + newPoints + '</td><td>  <button class="btn btn-danger" onclick="deleteOffer(' + r + ');">Delete</button></td><td> <button class="btn btn-warning" id="edit-' + r + '" onclick="toggleEdit(' + r + ');">Edit</button></td></tr>');
}});
}
function loadTable(type,pg) {
    var tableDisplay = document.getElementById("tabledisplay");
    tableDisplay.innerHTML = "<center><h3>Loading</h3></center>"
    $.ajax({url:"getTable", type:"POST", data:{tableType:type, page:pg}, success: function(r) {
	tableDisplay.innerHTML = r;
	document.getElementById("ttype").value = type;
	if (type == 1) {
	    var table = document.getElementById("disptable");
	    sorttable.makeSortable(table);
	    sorttable.innerSortFunction.apply(document.getElementById("namehead"),[]);
	}
    }});
}
function previewMessage() {
    var subject = document.getElementById("subject").value;
    var header = document.getElementById("header").value;
    var message = document.getElementById("message").value;
    var group = document.getElementById("group").options[document.getElementById("group").selectedIndex].value;
    $.ajax({url:"previewMessage", type:"POST", data:{subj:subject,head:header,msg:message,gr:group}, success: function(r) { 
	var previewWindow = window.open("http://www.fwbapp.com/preview","_blank","menubar=0,toolbar=0,location=0");
	previewWindow.onload = function(r2) {
	    previewWindow.document.getElementById("content").innerHTML = r;
	}
    }});
}

function sendMessage() {

    var payload = {};

    var subj = document.getElementById("subject").value;
    var head = document.getElementById("header").value;
    var mess = document.getElementById("message").value;
    payload.subject = subj;
    payload.header = head;
    payload.message = mess;

    var sendDate = document.getElementById("timepicker").value;
    payload.send = sendDate;
    var isRecur = document.getElementById("isRecur").checked;
    if (isRecur) {
	recurDays = document.getElementById("recurDay").value|0;
	payload.recur = recurDays;
    }

    var target_type = document.getElementById("recipType").selectedIndex;
    switch (target_type) {
	case 1: {
	    var g = document.getElementById("group").options[document.getElementById("group").selectedIndex].value;
	    payload.group = g;
	    break;
	}
	case 2: {
	    var idleDays = document.getElementById("idleDays").value|0;
	    payload.idledays = idleDays;
	}
    }

    var attachingOffer = document.getElementById("attachOffer").checked;
    if (attachingOffer) {
	var offername = document.getElementById("offername").value;
	payload.offname = offername;
	var isExpiring = document.getElementById("doesExpire").checked;
	console.log(isExpiring);
	if (isExpiring) {
	    var offerexp = document.getElementById("offerexp").value|0;
	    payload.offexp = offerexp;
	}
    }

    var valid = true;
    for (var k in payload) {
	valid &= !(payload[k] == "");
    }
    if (valid)
	$.ajax({url:"sendMessage",type:"POST",data:payload, success:function(r) {
	    alert(r);
	}});
    else
	alert("You did not fill out all the required fields.");
}

function addPoints(amnt,acc_id) {
    $.ajax({url:"addPoints",type:"POST",data:{user:acc_id,amount:amnt}, success: function(r) {
	if (r != '-') {
	    var v = document.getElementById("points-" + acc_id);
	    v.innerHTML = r;
	}
    }});
}


function editGroup(n) {
    var editButton = document.getElementById("edit-" + n);
    if (editButton.innerHTML == 'Edit') { // create edit field
	var groupNameContainer = document.getElementById("gnc-" + n);
	var groupName = groupNameContainer.children[0].innerHTML;
	groupNameContainer.innerHTML = '<input class="form-control field-inline" type="text" id="newGroupName" style="margin-bottom:10px;" value="' + groupName + '"></input>'
	editButton.className = editButton.className.replace("btn-warning","btn-success");
	editButton.innerHTML = "Save";
    }
    else { // post new group name
	var gnc = document.getElementById("gnc-" + n);
	var newGroupName = gnc.children[0].value;
	$.ajax({url:"updateGroupName",type:"POST",data:{gid:n,name:newGroupName},success:function(r) {
	    editButton.className = editButton.className.replace("btn-success","btn-warning");
	    editButton.innerHTML = "Edit";
	    gnc.innerHTML = '<h3 style="display:inline;margin-right:10px;">' + newGroupName + '</h3>';
	}});
    }
}

function deleteGroup(n) {
    var gname = document.getElementById("gnc-" + n).children[0].innerHTML;
    var willDelete = confirm("The group \"" + gname + "\" will be deleted permanently. Is that okay?")
    if (willDelete) {
	$.ajax({url:"deleteGroup",type:"POST",data:{gid:n},success:function(r) {
	    window.location.reload()
	}});
    }
}

function toggleRecur() {
    var ch = document.getElementById("isRecur");
    var area = document.getElementById("recurDayArea");
    if (ch.checked) $('#recurDayArea').show();
    else $('#recurDayArea').hide();
}
function toggleRecip() {
    var ch = document.getElementById("recipType");
    var si = ch.selectedIndex;
    $('#groupselect').hide();
    $('#daypicker').hide();
    $('#Recur').show();
    if (si == 1) $('#groupselect').show();
    else if (si == 2) {
	$('#daypicker').show();
    }
}
function toggleOfferAttach() {
    var ch = document.getElementById("attachOffer");
    if (ch.checked) $('#offerattachment').show();
    else $('#offerattachment').hide();
}
function toggleOfferExp() {
    var ch = document.getElementById("doesExpire");
    if (ch.checked) $('#offerExpHours').show();
    else $('#offerExpHours').hide();
}

function unsub(gid,cid) {
    $.ajax({url:"unsubFromGroup",type:"POST",data:{g:gid,t:cid},success: function(r) {
	var e = document.getElementById('c-' + cid);
	e.parentNode.removeChild(e);
	var subs = $('#cbody-'+gid).children().length;
	if (subs == 1) {
	    document.getElementById("mod-"+gid).children[0].innerHTML = subs + " Customer is in this group";
	}
	else {
	    document.getElementById("mod-"+gid).children[0].innerHTML = subs + " Customers are in this group";
	}
	var r = $('#newrow-'+gid);
    }});
}

function newRow(gid) {
    var t = $('#cbody-'+gid);
    t.append("<tr id='newrow-"+gid+"'>" + '<td><input id="newfn-'+gid+'" placeholder="Full Name" type="text" class="form-control" style="width:90%;"></input></td>' + '<td><input id="newpn-'+gid+'" placeholder="Phone #" type="text" class="form-control" style="width:90%;"></input></td>' + '<td><input id="newem-'+gid+'" placeholder="Email" type="text" class="form-control" style="width:90%;"></input></td>' + "<td><button onclick='saveRow("+gid+");' class='btn btn-success btn-xs'>Save</button></td></tr>");
    $('#a-'+gid).hide();
}
function saveRow(gid) {
    var newRow = $('#newrow-'+gid);
    var newfn = $('#newfn-'+gid).val();
    var newpn = $('#newpn-'+gid).val();
    var newem = $('#newem-'+gid).val();
    $.ajax({url:"saveRow",type:"POST",data:{group:gid,fn:newfn,pn:newpn,em:newem}, success: function(r) { 
	var re = r.split("\n");
	console.log(r);
	if (re[0] == "Success!") {
	    var tid = re[1];
	    var subs = $('#cbody-'+gid).children().length;
	    if (subs == 1) {
		document.getElementById("mod-"+gid).children[0].innerHTML = subs + " Customer is in this group";
	    }
	    else {
		document.getElementById("mod-"+gid).children[0].innerHTML = subs + " Customers are in this group";
	    }
	    var r = $('#newrow-'+gid);
	    console.log(r);
	    r.attr('id','c-'+tid);
	    var c = r.children();
	    console.log(c);
	    for (var x = 0; x < c.length-1; x++) {
		console.log(c[x].children[0]);
		c[x].innerHTML = re[x+2]
	    }
	    c[c.length-1].innerHTML = '<td><button class="btn btn-danger btn-xs" onclick="unsub('+gid+','+tid+');">-</button></td>'
	$('#a-'+gid).show();
	}
	else if (re[0] == 'Same') {
	    $('#newrow-'+gid).remove();
	    $('#a-'+gid).show();
	}
	else {
	    alert(r); 
	}
    }});
}

function loadModal(cid) {
    $.ajax({url:"loadGroups",type:"POST",data:{id:cid},success: function(r) {
	var lines = r.split("\n");
	var mb = $('#modal-body');
	for (var x = 0; x < lines.length; x+=3) {
	    var gname = lines[x];
	    var gid = lines[x+1];
	    var gsubbed = (lines[x+2] == 'y');
	    mb.append('<label for="check-'+gid+'">'+gname+'</label> <input id="check-'+gid+'" type="checkbox" onchange="toggleSub(this.checked,'+gid+','+cid+');"><br><br>');
	    document.getElementById("check-"+gid).checked = gsubbed;
	}
    }});
}    

function toggleSub(subbed,gid,cid) {
    var u = "subToGroup";
    if (!subbed) u = "unsubFromGroup";
    $.ajax({url:u,type:"POST",data:{g:gid,t:cid}, success:function(r){}});
}

function toggleDPP(checked) {
    $('#dppAmount').prop('disabled',!checked);
}

//
// AJAX Requests
//

function delJob(jid) {
    $.ajax({url:"deleteMailJob",type:"POST",data:{id:jid}, success: function(r) {
	var e = document.getElementById(jid);
	e.parentNode.removeChild(e);
    }});
}

function saveBGcolor(c) {
    $.ajax({url:"updateMainColor",type:"POST",data:{color:c.toHexString()}, success: function(r) { alert(r); }});
}

function saveHLcolor(c) {
    $.ajax({url:"updateHighlightColor",type:"POST",data:{color:c.toHexString()}, success: function(r) { alert(r); }});
}

function savePromo(newpromo) {
    $.ajax({url:"updatePromoText",type:"POST",data:{text:newpromo}, success: function(r) { alert(r); }});
}

function deleteOffer(offerid) {
    $.ajax({url: "deleteOffer", type:"POST", data:{offer_id:offerid}, success: function(r) { var element = document.getElementById(offerid); element.parentNode.removeChild(element); }});
}

function setStorename(newname) {
    $.ajax({url: "setStoreName", type:"POST", data:{name:newname}, success: function(r) { alert(r); if (r == "Success!") {document.getElementById("storename").placeholder = newname; document.getElementById("storename").value = "";}}});
}

function setPin(newpin) {
    $.ajax({url: "setPin", type:"POST", data:{pin:newpin}, success: function(r) { alert(r); if (r == "Success!") { var v = document.getElementById("newpin"); v.placeholder = newpin; v.value = "";}}});
}

function setPasswd(newPass,checkPass) {
    $.ajax({url: "setPasswd", type:"POST", data:{newpass:newPass,checkpass:checkPass}, success: function(r) { alert(r); document.getElementById("newpass").value = ""; document.getElementById("checkpass").value = "";} });
}

function setWait(newWait) {
    $.ajax({url: "setWaitTime", type:"POST", data:{wait:newWait}, success: function(r) { alert(r); }});
}

function saveDPP(any,amnt) {
    if (!any) amnt = -1;
    $.ajax({url: "setDollarPoints", type:"POST", data:{amount:amnt}, success: function(r) { alert(r); }});
}

//
// Char limits
//
function subjectLimit() {
    var c = document.getElementById("subject");
    if (c.value.length > 30)
	c.value = c.value.substring(0,30);
}
function headerLimit() {
    var c = document.getElementById("header");
    if (c.value.length > 30)
	c.value = c.value.substring(0,30);
}
function messageLimit() {
    var c = document.getElementById("message");
    if (c.value.length > 140)
	c.value = c.value.substring(0,140);
}
function offerNameLimit() {
    var c = document.getElementById("offername");
    if (c.value.length > 30)
	c.value = c.value.substring(0,30);
}
