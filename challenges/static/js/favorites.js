
CM.Favorite = {};

CM.Favorite.Handlers =  {
	init: function () {
		this.initListeners()
		this.setupFavoriteChallengesTab()
	},

	initListeners: function () {
		$(document.body).on('click', '.favorite', {me: this}, this.callback);
	},

	callback: function (e) {
		e.preventDefault();

		var me = e.data.me;
		var target = $(e.currentTarget);
		if ( target.hasClass("favorited") ) {
			$.post(target.attr('data-clear-url')).done( function (result) {
				if (result.success) {
					me.unfavorited(target);
				}
			});
		}
		else {
			$.post(target.attr('data-set-url')).done( function (result) {
				if (result.success) {
					me.favorited(target);
				}
			});
		}
	},

	unfavorited: function (target) {
		// var icon = target.find('span.icon');
		target.parent().parent().find('.favorite-badge-backfold').removeClass('active');
		target.find('.favorite-badge-content').removeClass('active');
		target.find('.favorite-badge-icon-plus').removeClass('hide');
		target.removeClass("favorited");
		// icon.removeClass("glyphicon-minus").addClass("glyphicon-plus");
	},

	favorited: function (target) {
		// var icon = target.find('span.icon');
		console.log(target)
		target.parent().parent().find('.favorite-badge-backfold').addClass('active');
		target.find('.favorite-badge-content').addClass('active');
		target.find('.favorite-badge-icon-plus').addClass('hide');
		target.addClass("favorited");
		// icon.removeClass("glyphicon-plus").addClass("glyphicon-minus");
	},

	setupFavoriteChallengesTab: function () {
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
};



$(document).ready(function () {
	CM.Favorite.Handlers.init();
});