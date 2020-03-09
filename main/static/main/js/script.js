console.log("Connected to JS!");

function validate()
{
	console.log("Running validate()!");

	// Validating City
	var city = document.getElementById('city').value;
	if(city.length > 20)
	{
		document.getElementById('city').style.border = '1px solid red';
		document.getElementById('errorMsgCity').innerHTML = 'Enter a valid city or place name!';
		document.getElementById('errorMsgCity').style.color = 'red';
		return false;
	}

	// Validating Radius
	var cgpa = document.getElementById('radius').value;
	if(radius<0 || radius>20)
	{
		document.getElementById('radius').style.border = '1px solid red';
		document.getElementById('errorMsgRadius').innerHTML = 'Enter a valid radius! (between 0.1km to 20km)';
		document.getElementById('errorMsgRadius').style.color = 'red';
		return false;
	}	

	document.getElementById('warnMsg').innerHTML = 'Please wait, it may take several minutes to fetch the data. <br><br>';
	document.getElementById('warnMsg').style.color = 'red';

	// If all validations are complete, return true
	return true;
}