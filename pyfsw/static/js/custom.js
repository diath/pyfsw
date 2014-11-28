$(function() {
	$.get('/messages', function(data) {
		if(!data.length) return;

		$('#messages').show();
		$('#messages').append(data);
	});
});
