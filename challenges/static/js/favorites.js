$(function(){
  $("input[data-toggle='favorite']").change(function(){
    var url = $(this).attr(this.checked ? 'data-set-url' : 'data-clear-url');
    $.post(url).done(function(result){
      if (!result.success) ; // TODO: error handling
    });
  });
});

function setupFavoriteChallengesTab() {
	$('a[data-toggle="tabajax"]').on('show.bs.tab', function (e) {
		var $this = $(e.target),
				loadurl = $this.attr('href'),
				targ = $this.attr('data-target');
		$(targ).html("");
	});
	$('a[data-toggle="tabajax"]').on('shown.bs.tab', function (e) {
		var $this = $(e.target),
				loadurl = $this.attr('href'),
				targ = $this.attr('data-target');

		$.get(loadurl, function(data) {
				$(targ).html(data);
				$(targ).children().owlCarousel({
					items : 4,
					itemsCustom : false,
					itemsDesktop : [1199,3],
					itemsDesktopSmall : [980,3],
					itemsTablet: [768,2],
					itemsTabletSmall: false,
					itemsMobile : [479,1],
					singleItem : false,
					itemsScaleUp : false
			});
		});
	});
}