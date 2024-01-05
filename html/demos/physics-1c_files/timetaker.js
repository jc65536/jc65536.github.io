var labelNode    = null;
var questionNode = null;
var answerArea   = null;

function initTimeTaker()
{

	dojo.addClass(questionNode, "invisible");
	if (answerArea.innerHTML == "")
	{
		answerArea.innerHTML = Date.now();
	}
	else
	{
		var tmpSave          = answerArea.innerHTML;
		var tempDate         = Date.now() - tmpSave;
		answerArea.innerHTML = tempDate;
	}
}

function initNodeVars()
{
	require(["dojo/query"], function (query)
	{
		var openQuestionNodes = query(".type_open_question label").forEach(function (node)
		{
			if (node.innerHTML == "[TIME-SPAN]")
			{
				labelNode    = node.parentNode;
				questionNode = labelNode.parentNode;
				answerArea   = query("textarea", questionNode);
				if (answerArea[0] != null)
				{
					answerArea = answerArea[0];
				}
			}
		});
	});
}

function submitAndTakeTime()
{
	var oSubmit = document.getElementsByName('btnsubmit')[0];
	if (oSubmit)
	{
		oSubmit.addEventListener('click', function ()
		{
			var startDate = answerArea.innerHTML;
			var duration  = Date.now() - startDate;
			var date      = new Date(null);
			date.setMilliseconds(duration);
			answerArea.innerHTML = date.toISOString().substr(11, 8);
		});
	}
}

function tempSaveTime()
{
	var orgsavetemp = savetemp;
	savetemp        = function ()
	{
		var startDate        = answerArea.innerHTML;
		var duration         = Date.now() - startDate;
		answerArea.innerHTML = duration;
		return orgsavetemp();
	}
}

require(["dojo/ready"], function (ready)
{
	ready(function ()
	{
		initNodeVars();
		if (labelNode != null && answerArea != null)
		{
			initTimeTaker();
			submitAndTakeTime();
			tempSaveTime();
		}
	});
});
