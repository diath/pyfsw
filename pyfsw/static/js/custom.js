$(function() {
	$.get('/messages', function(data) {
		if(!data.length) return;

		$('#messages').show();
		$('#messages').append(data);
	});

	$.get('/status', function(data) {
		if(!data.length) return;

		$('#status').popover({content: data, html: true, placement: 'top'});
		$('#status').popover('show');
	});
});
