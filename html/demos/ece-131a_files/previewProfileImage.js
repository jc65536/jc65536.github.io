function showPreviewImg(img, isOnline)
{
	if(isOnline == undefined)
	{
		isOnline = false;
	}
	
	if(isOnline)
	{
		img.style.width = "120px";
		img.style.height = "120px";	
	}
	else
	{
		var hiddenId = img.id+"_hidden";
		var hiddenimg = document.getElementById(hiddenId);
		var posY = img.getBoundingClientRect().bottom + window.scrollY;
		var posX = img.getBoundingClientRect().right + window.scrollX;
		hiddenimg.style.top = posY + "px";
		hiddenimg.style.left = posX + "px";	
		hiddenimg.style.display = "";	
	}
	
									
}
function hidePreviewImg(img, isOnline)
{
	if(isOnline == undefined)
	{
		isOnline = false;
	}
	if(isOnline)
	{
		img.style.width = "100%";
		img.style.height = "100%";
	}
	else
	{
		var hiddenId = img.id+"_hidden";
		var hiddenimg = document.getElementById(hiddenId);
		hiddenimg.style.display = "none";
	}
}