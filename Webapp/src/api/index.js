import axios from 'axios'
const API_URL = 'http://localhost:8983/solr/ir/'

// Fetches the results for a query 
// Upon receving response, check if results are found
// If results are not found, do a spell check and return first 3 results from the correct spellings 
export function helloworld(query){
	var URL = API_URL+"select?"+query+"&rows=50"
	return axios.get(URL).then(function (response){
		console.log("[API]: URL: "+URL)
		console.log("[API]: Received responses:" + response.data.response.numFound)
		return response.data.response
	}).catch(function (error){
		console.log(error)
	})
}

// Checks the spelling 
// http://localhost:8983/solr/ir/spell?q=trumep&sort=tweet_fav_count%20desc
export function checkSpelling(query){
	console.log("[API]: Spell check for: "+query)
	return axios.get(API_URL+"spell?df=tweet_text&q="+query).then(function (response){
		console.log("[API]: URL "+API_URL+"spell?df=tweet_text&q="+query)
		var numOfCollations = response.data.spellcheck.collations.length
		console.log("[API]: Received responses:" +numOfCollations) // Change
		var suggestion = null;
		if(numOfCollations >= 2){
			suggestion = response.data.spellcheck.collations[1].collationQuery
		}
		return suggestion //change to array of corrections 
	}).catch(function(error){
		console.log(error)
	})
}

export function searchMultipleQuery(queryList){
	console.log("[API]: Searching multiple queries of size: "+queryList.length)
	var ps = [];
	for (let i = 0; i < queryList.length; i++){
		ps.push(helloworld(queryList[i].word))
	}
	return Promise.all(ps).then((results) => {
		console.log(results)
		return results
	}).catch(function(error){
		console.log(error)
	})
}