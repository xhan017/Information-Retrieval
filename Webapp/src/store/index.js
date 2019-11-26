import Vue from 'vue'  
import Vuex from 'vuex'
import {
	helloworld,
  checkSpelling,
  searchMultipleQuery
} from '@/api'

Vue.use(Vuex)

const state = {  
  // single source of data
  results: [],
  spellCheckSuggestion: ''
}

const actions = {  
  // asynchronous operations


  // Search with query text
  getSearch(context, dic) {
    helloworld(getQuery(dic)).then((response) => 
      context.commit('setResults', { results: response })
      ).then(function(){
      // If we have insufficient results, do a spell check
      if(state.results != null){
        console.log("[Store]: state.results.size = "+state.results.numFound)
      if(state.results.numFound <= 0){
        console.log("[Store]: No results.")
        checkSpelling(dic.query).then((response) => 
          context.commit('setSpellCheckSuggestion', {spellCheckSuggestion: response})
          )
      }else{
        context.commit('setSpellCheckSuggestion', {spellCheckSuggestion: null})
      }
      }
    }).then(function(){
      // For the first 3 the suggested corrections, find query results 
    })
  }
}

const mutations = {  
  // isolated data mutations
  setResults(state, payload){
  	console.log("Received response")
  	// After we get the response, we need to process the data first. 
  	state.results = payload.results
  	console.log(state.results)
  },

  setSpellCheckSuggestion(state, payload){
    console.log("Received response")
    state.spellCheckSuggestion = payload.spellCheckSuggestion
    console.log(state.spellCheckSuggestion)
  }
}

const getters = {  
  // reusable data accessors
}

const store = new Vuex.Store({  
  state,
  actions,
  mutations,
  getters
})

export default store 


// searchParameters: { query: this.queryText, sorting: this.postSorting, category: this.postFiltering, handlers: this.handlerFiltering}
function getQuery(dictionary){
  // Query
  var queryString = "&q="+dictionary.query

  // Sorting
  if(dictionary.sorting != ''){
    queryString += "&sort="+dictionary.sorting
  }
  
  // &fq=(screen_name: WSJ OR screen_name:DEF) OR (screen_name: ABC)
  queryString+="&fq="
  var conditional = ""
  // Category
  console.log("Category length: "+dictionary.category.length)
  if(dictionary.category.length >= 1 && dictionary.category[0].length>1){
    conditional += "("
    for(let i = 0; i < dictionary.category.length; i++){
      if(i >= 1){
        conditional += " OR "
      }
      conditional += "category:"+dictionary.category[i]
    }
    conditional += ")"
  }

  // Handler
  if(dictionary.handlers.length >=1){
    if(dictionary.category.length >= 1 && dictionary.category[0].length>1){
      conditional += " AND "
    }
    conditional += "("
    for(let i = 0; i < dictionary.handlers.length; i++){
      if(i >= 1){
        conditional += " OR "
      }
      conditional += "screen_name:"+dictionary.handlers[i]
    }
    conditional += ")"
  }

  conditional = "("+conditional+")"
  queryString+=conditional
  queryString+="&df=tweet_text"

  // queryString = queryString.replace(' ', '%20')
  console.log(queryString)
  return queryString
}