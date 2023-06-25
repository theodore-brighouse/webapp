function search(query) {
    // update the input field to equal the query
    document.getElementById("search-input").value = query;
    // remove any genre selections
    document.getElementById("genre-dropdown").value = 0;
    // set the url to the corrosponding search query
    var newURL = "search?q=" + encodeURIComponent(query);
    window.history.replaceState({ path: newURL }, "", newURL);
    // create a new xhttp request and have 'search-results' receive the response
    var xhttp; 
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
                document.getElementById("search-results").innerHTML = this.responseText;
        }
    };
    // if the query is empty, set the url to browse and return 'browse-content' to 'search-results'
    if (query.trim() == "") {
        document.getElementById("search-results").innerHTML = "";
        var newURL = "browse";
        window.history.replaceState({ path: newURL }, "", newURL);
        xhttp.open("POST", "browse-content", true);
        return xhttp.send();
    }
    // return the results of the query 
    xhttp.open("POST", "search-results?q=" + query, true);
    return xhttp.send();
}

function genre(query) {
    // update the dropdown to equal the query
    document.getElementById("genre-dropdown").value = query;
    // remove any search feild inputs
    // set the url to the corrosponding genre search query
    var newURL = "genre?q=" + encodeURIComponent(query);
    window.history.replaceState({ path: newURL }, "", newURL);
    // create a new xhttp request and have 'search-results' receive the response
    var xhttp;
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("search-results").innerHTML = this.responseText;
        }
    };
    // if the dropdown value is 0, set the url to browse and return 'browse-content' to 'search-results'
    if (query == 0) {
        document.getElementById("search-results").innerHTML = "";
        var newURL = "browse";
        window.history.replaceState({ path: newURL }, "", newURL);
        xhttp.open("POST", "browse-content", true);
        return xhttp.send();
    }
    // return the results of the genre query
    xhttp.open("POST", "genre-results?q=" + query, true);
    return xhttp.send();
}

function browse() {
    var xhttp;
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("search-results").innerHTML = this.responseText;
        }
    };
    xhttp.open("POST", "browse-content", true);
    return xhttp.send();
}