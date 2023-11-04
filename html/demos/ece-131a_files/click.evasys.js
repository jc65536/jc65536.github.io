function Fensterweite ()
{
	if (window.innerWidth)
	{
		return window.innerWidth;
  	}
  	else if (document.body && document.body.offsetWidth)
  	{
    	return document.body.offsetWidth;
  	}
  	else
  	{
    	return 0;
  	}
}

function Fensterhoehe ()
{
  	if (window.innerHeight)
  	{
    	return window.innerHeight;
  	}
  	else if (document.body && document.body.offsetHeight)
  	{
    	return document.body.offsetHeight;
  	}
  	else
  	{
    	return 0;
  	}
}

function neuAufbau(bGo)
{
	if(typeof bGo == 'undefined') bGo = false;
	
	if (Weite != Fensterweite() || Hoehe != Fensterhoehe() || bGo)
  	{
		if (document.getElementById('adminrightalignedwrapper'))
		{
			var adminrightalignedwrapper = document.getElementById('adminrightalignedwrapper');
			adminrightalignedwrapper.style.right = "2";
			adminrightalignedwrapper.style.right = "1";
		}
		if (document.getElementById('userrightalignedwrapper'))
		{
			var adminrightalignedwrapper = document.getElementById('userrightalignedwrapper');
			adminrightalignedwrapper.style.right = "2";
			adminrightalignedwrapper.style.right = "1";
		}
 	}
}

function correctWidthByContent()
{
	var nOverallWidth = document.getElementById('maintable').offsetWidth;
	if (nOverallWidth > 5000)
	{
		var nCenterWidth = nOverallWidth - 2002;
		document.getElementById('adminheadstart').style.width = "999px";
		document.getElementById('adminheadcenter').style.width = nCenterWidth.toString() + "px";
		document.getElementById('adminheadend').style.width = "999px";
	}
	document.getElementById('adminheadmenu').style.width = nOverallWidth;
	
}

/**
 * @param {*} btn
 * @param {*} title
 * @param {string} target
 * @param {boolean} bSubmit
 * @param {string} sConfirmationText
 * @param {boolean} bValidate
 * @param {string} errorMessage
 */
function disableButton(btn, title, target, bSubmit, sConfirmationText, bValidate, errorMessage)
{
	if(bValidate && !validateHTMLForm(btn, errorMessage)) {
		return false;
	}

	if(typeof bSubmit == 'undefined') bSubmit = true;
	if(typeof sConfirmationText == 'undefined') sConfirmationText = '';

	var bConfirm = true;
	if (sConfirmationText != '')
	{
		bConfirm = confirm(sConfirmationText);
	}
	
	if (bConfirm)
	{
		if (title)
		{
			btn.value = title;
			if (!btn.style.width)
			{
				btn.style.width = "100px";
			}
		}
		btn.disabled = true;
		btn.style.cursor = "wait";

		if (bSubmit)
		{
			if(target)
			{
				location.href = target;
			}
			else
			{
				btn.form.submit();
			}
		}
		return true;
	}
	else
	{
		return false;
	}
}

/**
 * @param btn
 * @param {string} errorMessage
 * @returns {boolean}
 */
function validateHTMLForm(btn, errorMessage)
{
	if (!btn.form.checkValidity())
	{
		if (btn.form.reportValidity)
		{
			btn.form.reportValidity();
		}
		else
		{
			alert(errorMessage); // reportValidity is not supported in IE
		}
		return false;
	}
	return true;
}

/*
* Calls an URL via AJAX with GET
*/
function ajaxCall(sUrl, sHandleAs, nTimeOut, sLayer, sAlertOnFail, bSync)
{
	if(typeof sUrl == 'undefined') return;
	if(typeof sHandleAs == 'undefined') sHandleAs = "text";
	if(typeof nTimeOut == 'undefined') nTimeOut = 5000;
	if(typeof sLayer == 'undefined') sLayer = '';
	if(typeof sAlertOnFail == 'undefined') sAlertOnFail = '';
	if(typeof bSync == 'undefined') bSync = false;

	var bSuccess = 1;
	var sResponse = dojo.xhrGet({
		url: sUrl,
		handleAs: sHandleAs,
		timeout: nTimeOut,
		sync: bSync,
		load: function(response, args) {
			if (sLayer != '')
			{
				if (dojo.byId(sLayer).nodeName.toUpperCase() == "SELECT")
				{
					//workaround for IE adding options to SELECT
					var sOuterHTML = dojo.byId(sLayer).outerHTML;
					sOuterHTML = sOuterHTML.replace("</select>", "");
					sOuterHTML = sOuterHTML.replace("</SELECT>", "");
					dojo.byId(sLayer).outerHTML = sOuterHTML + response + "</select>";
				}
				else
				{
					dojo.byId(sLayer).innerHTML = response;
				}
			}
			return response;
		},
		error: function(response, args) {
			console.log("Failed xhrGet", response, args);
			bSuccess = 0;
			return response;
		}
	});

	if (bSuccess == 0 && sAlertOnFail != '')
	{
		alert(sAlertOnFail);
	}

	return sResponse;
}

function ajaxCallPost(sUrl, oPostData, sHandleAs, nTimeOut, bSync, sLayer, sAlertOnFail)
{
	if(typeof sUrl == 'undefined') return;
	if(typeof oPostData == 'undefined') oPostData = "";
	if(typeof sHandleAs == 'undefined') sHandleAs = "text";
	if(typeof nTimeOut == 'undefined') nTimeOut = 5000;
	if(typeof bSync == 'undefined') bSync = false;
	if(typeof sLayer == 'undefined') sLayer = '';
	if(typeof sAlertOnFail == 'undefined') sAlertOnFail = '';

	var bSuccess = 1;
	var sResponse = dojo.xhrPost({
		url: sUrl,
		content: oPostData,
		handleAs: sHandleAs,
		timeout: nTimeOut,
		sync: bSync,
		load: function(response, args) {
			if (sLayer != '')
			{
				if (dojo.byId(sLayer).nodeName.toUpperCase() == "SELECT")
				{
					//workaround for IE adding options to SELECT
					var sOuterHTML = dojo.byId(sLayer).outerHTML;
					sOuterHTML = sOuterHTML.replace("</select>", "");
					sOuterHTML = sOuterHTML.replace("</SELECT>", "");
					dojo.byId(sLayer).outerHTML = sOuterHTML + response + "</select>";
				}
				else if (dojo.byId(sLayer).nodeName.toUpperCase() == "IFRAME")
				{
					dojo.byId(sLayer).contentDocument.write(response);
				}
				else
				{
					dojo.byId(sLayer).innerHTML = response;
				}
			}
			return response;
		},
		error: function(response, args) {
			console.log("Failed xhrPost", response, args);
			bSuccess = 0;
			return response;
		}
	});

	return bSuccess;
}

/*
 * This function calls a url with post data and returns the result as json. It does not change anything in the html
 */
function ajaxCallPostAndReturn(url , oPostData,sHandleAs, nTimeOut, bSync)
{
	var sLayer = '';
	var sAlertOnFail = '';
		
	var bSuccess = 1;
	var result = "";
	
	if(typeof sHandleAs == 'undefined') sHandleAs = "json";
		
	if(typeof bSync == 'undefined') bSync = true; // most of the time it should be true.
	
	var oResponse = dojo.xhrPost({
		url: url,
		content: oPostData,
		handleAs: sHandleAs,
		timeout: nTimeOut,
		sync: bSync,
		load: function(response, args) {
			result = response;
		},
		error: function(errorMessage) {
			
			console.log("Failed xhrPost:"+errorMessage);
			result = "error";
			return errorMessage;
		},
		
	});
	
	return result;	
}

	
/**
 * getFormData() gathers form element data into an array of objects that can
 * be passed to ajaxCallPost()
 */
function getFormData(theform)
{
	var oPostData = {};

	for(n=0; n < theform.elements.length; n++)
	{
		if (!theform.elements[n].name)
		{
			continue;
		}

		formName  = theform.elements[n].name; 
		formValue = fieldValue(theform.elements[n]);

		if (formValue != null )
		{
			if (oPostData[formName] != null)
			{
				if (oPostData[formName].constructor != Array)
				{
					var sTmp = oPostData[formName];
					oPostData[formName] = new Array(sTmp);
				}
				oPostData[formName].push(formValue);
			}
			else
			{
				oPostData[formName] = formValue;
			}
		}
	}

	return oPostData;
}


/**
 * allows to fold and unfold groups of listitems (used in the menu for subunits)
 */
function togglefolding(nodeItem,url)
{
	var timing = 0;
	var sNewDisplayValue = 'none';
	var sIcon = 'images/icons/order_right.png';
	var nodeMenu = nodeItem.parentNode.parentNode;
	
	var oPostData= [];

	
		
	if (nodeMenu.className.indexOf('closed') > -1)
	{
		sNewDisplayValue = 'block';
		sIcon = 'images/icons/order.png';
		nodeMenu.className = nodeMenu.className.split(/ closed/).join(' ');
		
		oPostData['closedstatus'] = 0; // open
		
	}
	else
	{
		sNewDisplayValue = 'none';
		sIcon = 'images/icons/order_right.png';
		nodeMenu.className += ' closed';
		
		oPostData['closedstatus'] = 1; // closed
		
	}
	
	var nodes = nodeMenu.childNodes;
	for (var i = 0, len = nodes.length; i < len; i++)
	{
		if (undefined !== nodes[i].className && nodes[i].className.indexOf('foldable') > -1)
		{
			var subnode = nodes[i];
			setTimeout((function(node) { return function() { node.style.display = sNewDisplayValue;}}(subnode)), 2*(len-i));
		}
	}
	
	nodes = nodeItem.childNodes;
	for (var i = 0, len = nodes.length; i < len; i++)
	{
		if (nodes[i].nodeName == 'IMG')
		{
			nodes[i].src = sIcon;
		}
	}
	
	ajaxCallPost(url,oPostData);
	
	return true;
}
		
/**
 * Returns the value of the field element.
 */
var fieldValue = function(el) {
	var n = el.name, t = el.type, tag = el.tagName.toLowerCase();

	if (!n || el.disabled || t == 'reset' || t == 'button' ||
		(t == 'checkbox' || t == 'radio') && !el.checked ||
		(t == 'submit' || t == 'image') && el.form && el.form.clk != el ||
		tag == 'select' && el.selectedIndex == -1) {
			return null;
	}

	if (tag == 'select') {
		var index = el.selectedIndex;
		if (index < 0) {
			return null;
		}
		var a = [], ops = el.options;
		var one = (t == 'select-one');
		var max = (one ? index + 1 : ops.length);
		for (var i = (one ? index : 0); i < max; i++) {
			var op = ops[i];
			if (op.selected) {
				var v = op.value;
				if (!v) { // extra pain for IE...
					v = (op.attributes && op.attributes['value'] &&
							!(op.attributes['value'].specified)) ?
							op.text : op.value;
			}
				if (one) {
					return v;
				}
				a.push(v);
			}
		}
		return a;
	}
	return el.value;
};

/**
 * Closes window even for firefox.
 *
 * Firefox won't close the window if it isn't opened by a script, because of
 * security reasons. With a little hack we ensure that the window is closed.
 */
function closeWindow()
{
	window.close();

	// If our window wasn't closed by then, firefox probably blocked it.
	// If we open a new window ontop of the current one and close our window,
	// we closed our new window and the current we were actually trying to close
	setTimeout(function()
	{
		window.open('', '_parent', '');
		window.close();
	}, 25);
}
