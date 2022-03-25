$(document).ready(function() {
	$('tr').click(function() {
		$(this).next('.details-row').toggleClass('tr-collapse');
	});
});