<template>
	<div>
		<div id="parallax" class="ui  container segment" style="width: 100%; padding-top: 15%; height: 100vh;">
			<img src="">
			<!--
				<video class="visible-desktop" id="hero-vid"  autoplay loop muted>
					<source type="video/webm" src="https://www.videvo.net/videvo_files/converted/2015_10/preview/Smartphone_scroll_02_Videvo.mov95221.webm"></source>
				</video>
			-->
			<div class="ui orange segment" style="margin: 0 auto; width: 50%; padding: 70px; background-color: white">
				<div class="ui grid">
					<div class="row">
						<h2 class="ui left aligned header" style="font-size: 45px">
							<img src="./twitter_logo.jpg" class="ui image">
							<div class="content">
								CZ4034 - Information Retrieval
								<div class="sub left aligned header" style="font-size: 30px">
									Search for tweets most <font color="#E84214">relevant</font> to you 
								</div>
							</div>
						</h2>
					</div>
					<div class="row">
						<!-- Simple search bar -->
						<div class="ui large centered action input" data-children-count="1" style="width: 100%">
							<input type="text" placeholder="Search..." v-model="queryText" @keyup.enter="enter">
							<button class="ui basic positive button" @click="search()" v-bind:class="(queryText.length >= 1)?'ui basic positive button':'ui basic disabled positive button'">
								Search
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
		<div class="ui basic segment" style="height: 100vh;" id="resultDiv" >
			<button class="ui basic green button" @click="topFunction()" id="myBtn" title="Go to top" style="position: fixed; bottom: 20px; right: 20%; display: none;">
				<i class="arrow circle up icon"></i>
				Back to top
			</button>
			<div class="ui centered grid" style="height: 85vh">
				<!-- Search box -->
				<div class="row">
					<div class="ui large centered action input" data-children-count="1" style="width: 50%; margin-top: 30px" v-scroll-reveal.reset="{ delay: 50, origin: 'left' }">
						<input type="text" placeholder="Search..." v-model="queryText" @keyup.enter="enter" v-bind:placeholder="this.queryText">
						<button class="ui basic black button" @click="search()" v-bind:class="(queryText.length >= 1)?'ui basic black button':'ui basic black disabled button'">
							Search
						</button>
					</div>
				</div>
				<!-- Filter tweets-->
				<div class="row" style="margin-top: -30px">
					<div class="ui left aligned grey basic segment" style="width:50%; padding: 10px; height: 20px" v-scroll-reveal.reset="{ delay: 50, origin: 'left' }">
						<div class="ui grid">
							<div class="ui ten wide left floated column">
								<div class="ui multiple dropdown" id="FilterDropdown">
									<input type="hidden" name="filters" id="CategoryID" @change="setCategoryFilter()">
									<span class="text"><i class="filter icon"></i>Filter Tweets</span>
									<div class="menu">
										<div class="ui icon search input">
											<i class="search icon"></i>
											<input type="text" placeholder="Search tags...">
										</div>
										<div class="divider"></div>
										<div class="header">
											<i class="tags icon"></i>
											Tag Label
										</div>
										<div class="scrolling menu">
											<div class="item" data-value="Business">
												<div class="ui red empty circular label"></div>
												Business
											</div>
											<div class="item" data-value="Entertainment">
												<div class="ui blue empty circular label"></div>
												Entertainment
											</div>
											<div class="item" data-value="Sport">
												<div class="ui black empty circular label"></div>
												Sport
											</div>
											<div class="item" data-value="Technology">
												<div class="ui purple empty circular label"></div>
												Technology
											</div>
											<div class="item" data-value="US">
												<div class="ui orange empty circular label"></div>
												US
											</div>
											<div class="item" data-value="World">
												<div class="ui green empty circular label"></div>
												World
											</div>
										</div>
									</div>
								</div>
							</div>
							<div class="ui right aligned six wide right floated column">
								<h4 class="ui header" style="margin-top: 5px">
									<div class="content">
										Sort posts by 
										<div class="ui inline dropdown" id="SortingDropdown">
											<div class="text"></div>
											<i class="dropdown icon"></i>
											<div class="menu">
												<div class="header">Sorting Options</div>
												<div class="active item" data-text="Favorites ascending" @click="setSortingType('tweet_fav_count asc')">Favorites ascending</div>
												<div class="item" data-text="Favorites descending" @click="setSortingType('tweet_fav_count desc')">Favorites descending</div>
												<div class="item" data-text="Retweets ascending" @click="setSortingType('tweet_retweet_count asc')">Retweets ascending</div>
												<div class="item" data-text="Retweets descending" @click="setSortingType('tweet_retweet_count desc')">Retweets descending</div>
												<div class="item" data-text="Creation date ascending" @click="setSortingType('tweet_creation asc')">Creation date ascending</div>
												<div class="item" data-text="Creation date descending" @click="setSortingType('tweet_creation desc')">Creation date descending</div>
												<div class="item" data-text="none" @click="setSortingType('')">None</div>
											</div>
										</div>
									</div>
								</h4>
							</div>
						</div>
					</div>
				</div>
				<!-- Search suggetsions -->
				<div class="row" >
					<div class="ui left aligned basic segment" style="width:50%; padding-top: 20px; height: 20px">
						<div class="ui breadcrumb">
							<div class="active section">
								<div v-if="i_results.numFound === 0">
									<div v-if="i_suggestions === null"> No suggestions!</div>
									<div v-else>Do you mean <a @click="searchCorrected(i_suggestions)">{{i_suggestions}}</a>?</div>
								</div>
							</div>
						</div>
					</div>
				</div>
				<!-- Main tweet display -->
				<div class="row" style="height: 100%;">
					<div class="ui basic segment" style="width: 50%; margin-top: 2px" >
						<div class="ui left dividing rail" v-scroll-reveal.reset="{ delay: 750, origin: 'left' }">
							<div class="ui basic segment">
								<div class="ui left aligned basic segment">
									<div class="ui secondary vertical pointing menu" id="HandlerFilterMenu">
										<a class="item active" style="height: 50px" value="CNN" @click="setHandlerFilter('CNN')">
											<h5 class="ui header">
												<img src="https://pbs.twimg.com/profile_images/925092227667304448/fAY1HUu3_400x400.jpg" class="ui circular image">
												CNN
											</h5>
											<div class="ui inverted dimmer" id="CNNDimmer"></div>
										</a>
										<a class="item active" style="height: 50px;" value="Eco" @click="setHandlerFilter('TheEconomist')">
											<h5 class="ui header">
												<img src="https://pbs.twimg.com/profile_images/879361767914262528/HdRauDM-_400x400.jpg" class="ui circular image">
												The Economist
											</h5>
											<div class="ui inverted dimmer" id="EcoDimmer"></div>
										</a>
										<a class="item active" style="height: 50px" value="BBCSports" @click="setHandlerFilter('BBCSport')">
											<h5 class="ui header">
												<img src="https://pbs.twimg.com/profile_images/968086146180886528/P_nvzGw__400x400.jpg" class="ui circular image">
												BBCSports
											</h5>
											<div class="ui inverted dimmer" id="BBCSportsDimmer"></div>
										</a>
										<a class="item active" style="height: 50px" value="WSJ" @click="setHandlerFilter('WSJ')">
											<h5 class="ui header">
												<img src="https://pbs.twimg.com/profile_images/971415515754266624/zCX0q9d5_400x400.jpg" class="ui circular image">
												Wall Street Journal
											</h5>
											<div class="ui inverted dimmer" id="WSJDimmer"></div>
										</a>
										<a class="item active" style="height: 50px" value="Verge" @click="setHandlerFilter('Verge')">
											<h5 class="ui header">
												<img src="https://pbs.twimg.com/profile_images/877903823133704194/Mqp1PXU8_400x400.jpg" class="ui circular image">
												Verge
											</h5>
											<div class="ui inverted dimmer" id="VergeDimmer"></div>
										</a>
									</div>
								</div>
								<div class="ui left aligned basic segment">
								</div>
							</div>
						</div>
						<div class="ui left aligned basic segment" >
							<div class="ui basic segment">
								<div class="ui grid">
									<div v-for="r in i_results.docs" v-bind:key="r.id">
										<div class="ui row">
											<div class="six wide column" style="margin-top: 10px">
												<div class="ui basic segment">
															<div v-if="r.category === 'Business'">
																<div class="ui red empty circular label"></div><b>  Category: {{r.category}}</b>
															</div>
															<div v-else-if="r.category === 'Entertainment'">
																<div class="ui blue empty circular label"></div><b>  Category: {{r.category}}</b>
															</div>
															<div v-else-if="r.category === 'Sport'">
																<div class="ui black empty circular label"></div><b>  Category: {{r.category}}</b>
															</div>
															<div v-else-if="r.category === 'Technology'">
																<div class="ui purple empty circular label"></div><b>  Category: {{r.category}}</b>
															</div>
															<div v-else-if="r.category === 'US'">
																<div class="ui orange empty circular label"></div><b>  Category: {{r.category}}</b>
															</div>
															<div v-else>	
																<div class="ui green empty circular label"></div><b>  Category: {{r.category}}</b>
															</div>
															<!-- cards: 'hidden',  -->
													<Tweet :id="r.id" :options="{ hide_thread: true, conversation: 'none', width: '380'}">
													</Tweet>
												</div>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
					<p></p>
				</div>
			</div>
		</div>
	</div>
</div>
</template>
<script>
	import { mapState } from 'vuex'  
	const VueScrollTo = require('vue-scrollto')
	
	Vue.use(VueScrollTo, {duration: 500, easing: "ease-in"})
	
	import JQuery from 'jquery'	
	import Tweet from 'vue-tweet-embed'
	
	let $ = JQuery
	jQuery('.ui.multiple.dropdown').dropdown();

	var selectedHandlers = []
	
	export default{
		name: 'Homepage',
		data(){
			return{
				queryText: '',
				fadeOnce: false,
				activeDisplay: [], // The active number of tweets to display. Limited to 50. 	
				pageNumber: 0, 
				type: 'A',
				postSorting: '',
				postFiltering: [], // category
				handlerFiltering: ['WSJ', 'CNN', 'TheEconomist', 'BBCSport', 'Verge'],	// screen_name
				searchParameters: { query: this.queryText, sorting: this.postSorting, category: this.postFiltering, handlers: this.handlerFiltering}
			}
		},
		computed: mapState({
			i_results: state => state.results,
			i_suggestions: state => state.spellCheckSuggestion
		}),
		components:{
			Tweet
		},
		beforeMount(){
			// this.results = "",
			// this.$store.dispatch('getSearch')
		},
		methods:{
			enter(){
				this.search()
				jQuery('.ui.multiple.dropdown').dropdown();
			},
			search(){
				console.log("searching for: "+this.queryText)
				// Update search params
				this.searchParameters = { query: this.queryText, sorting: this.postSorting, category: this.postFiltering, handlers: this.handlerFiltering}
				this.$store.dispatch('getSearch', this.searchParameters)
				$('html, body').animate({
					scrollTop: $("#resultDiv").offset().top
				}, 1000);
				// VueScrollTo.scrollTo('#resultDiv')
			},
			topFunction(){
				$('html, body').animate({
					scrollTop: $("#resultDiv").offset().top
				}, 1000);
			},
			searchCorrected(q){
				console.log("searching for: "+q)
				this.searchParameters = { query: q, sorting: this.postSorting, category: this.postFiltering, handlers: this.handlerFiltering}
				this.$store.dispatch('getSearch', this.searchParameters)
				$('html, body').animate({
					scrollTop: $("#resultDiv").offset().top
				}, 1000);
				this.queryText = q;
			},
			setHandlerFilter(handler){		// This sets the handler filters
				// If exists in the handler, remove 
				// Else, add
				if(this.handlerFiltering.includes(handler)){
					var position = this.handlerFiltering.indexOf(handler);
					this.handlerFiltering.splice(position, 1)
					console.log("[Homepage -> Handler]:  Removing handler: "+handler)
				}else{
					this.handlerFiltering.push(handler)
					console.log("[Homepage -> Handler]: Adding handler: "+handler)
				}
				console.log("[Homepage -> Handler]: Handler list: "+this.handlerFiltering)

				// Call search?
			},
			setCategoryFilter(category){	// This sets the category filters
				//'Business','Entertainment','Sport','Technology','US','World'
				var list = document.getElementById("CategoryID");
				this.postFiltering = list.value.split(",");
				console.log("[Homepage -> Category]: Category list: "+list.value)

				// Call search?
			},
			setSortingType(sorting){
				this.postSorting = sorting
				console.log("[Homepage -> Sorting]: Sorting type: "+this.postSorting)

				// Call search?
			}
		},
		watch: {
			queryText: function(){
				console.log("[Homepage]: "+this.queryText)
			},
			i_results: function(){
				console.log("[Homepage]: Received results!")
			}
		}
	}
	
	window.onload=function(){
		jQuery('#FilterDropdown').dropdown();
		jQuery('#SortingDropdown').dropdown();


		$('.ui.secondary.vertical.pointing.menu').on('click', '.item', function() {
			var dimmerID = $(this).attr('value')+"Dimmer";
			if($(this).hasClass('active')){
				$(this).removeClass('active');
				$('#'+dimmerID+'').addClass('active');
					}else{ // setting to active 
						$(this).addClass('active');
						$('#'+dimmerID+'').removeClass('active');
					}
				}); 

				//var x = document.getElementById("hero-vid");
				//x.playbackRate = 0.7;
			}

			window.onscroll = function() {scrollFunction()};

			function scrollFunction() {
				if (document.body.scrollTop > 1500 || document.documentElement.scrollTop > 1500) {
					document.getElementById("myBtn").style.display = "block";
				} else {
					document.getElementById("myBtn").style.display = "none";
				}
			}


		</script>
		<style>
		#parallax {
			/* The image used */
			background-image: url("geometry-abstract-minimalism-0x-2560x1440.jpg");
			/* Set a specific height */
			min-height: 500px; 
			/* Create the parallax scrolling effect */
			background-attachment: fixed;
			background-position: center;
			background-repeat: no-repeat;
			background-size: cover;
		}
		#hero-vid {
			backface-visibility:hidden;
			bottom:0;
			height:auto;
			min-height:100vh;
			min-width:100%;
			position:fixed;
			right:0;
			width:auto;
			filter:opacity(50%);
		}
		#resultDiv{
			background-color:white;
			padding:2.5rem;
			position:relative;
			z-index:1;
		}
	</style>