;(function (global) {

	'use strict';

	function Expounder() {

		var appearClass = 'expounded-appear',
			disappearClass = 'expounded-disappear';

		this.getScriptParams = function() {
			var scripts = document.getElementsByTagName('script');
			var scriptName = scripts[scripts.length - 1]; // always the current script
			return {
				defaultCollapse : scriptName.hasAttribute('data-default-collapse')
									? (scriptName.getAttribute('data-default-collapse') == "true")
									: false
			};
		};

		this.getElements = function() {
			return document.querySelectorAll('[data-expounder], [data-expounder-c]');
		};

		this.getExpoundedItems = function(id) {
			if (typeof id === 'undefined') {
				throw new Error("Missing Expounder id");
			}
			return document.querySelectorAll('[data-expounded="' + id + '"]');
		};

		this.animationEndListener = function(event) {

			if (event.target.className == disappearClass) {
				event.target.className = '';
			}

		};

		this.apply = function() {

			var expounder = this,
				elements = this.getElements();

			for (var index = 0; index < elements.length; index++) {

				var element = elements[index];

				if ((typeof element.dataset.expounderLoaded != 'undefined')) {
					continue;
				} else {
					element.dataset.expounderLoaded = true;
				}

				elements[index].addEventListener('click', function(event) {

					event.preventDefault();

					var defaultCollapse = expounder.getScriptParams().defaultCollapse,
						shouldContract = defaultCollapse || (typeof this.dataset.expounderC != 'undefined'),
						expoundId = this.dataset.expounder || this.dataset.expounderC,
						expoundedItems = expounder.getExpoundedItems(expoundId);

					for (var i = 0; i < expoundedItems.length; ++i) {

						var expounded = expoundedItems[i];

						if (shouldContract) {

							if (expounded.className == appearClass) {
								expounded.addEventListener('animationend', expounder.animationEndListener);
								expounded.className = disappearClass;
							} else {
								expounded.removeEventListener('animationend', expounder.animationEndListener);
								expounded.className = appearClass;
							}

						} else {

							expounded.className = appearClass;

						}
					}

					if (!shouldContract) {
						var parentNode = this.parentNode;
						var textNode = document.createTextNode(this.textContent);
						parentNode.replaceChild(textNode, this);
					}

				}, false);
			}

		};
	}

	// Export
	var expounder = new Expounder();

	// automatically apply it on load
	document.addEventListener('DOMContentLoaded', function() {
		expounder.apply();
	});

	// AMD
	if (typeof define === 'function' && define.amd) {

		define(function () {
			return expounder;
		});

		// Node and other CommonJS-like environments that support module.exports
	} else if (typeof module !== 'undefined' && module.exports) {

		module.exports = expounder;

		// Browser
	} else {
		global.Expounder = expounder;
	}

})(this);
