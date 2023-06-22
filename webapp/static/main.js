function search(query) {
    document.getElementById("search-input").value = query;
    document.getElementById("genre-dropdown").value = 0;
    var xhttp;
    var newURL = "search?q=" + encodeURIComponent(query);
    window.history.replaceState({ path: newURL }, "", newURL);
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
                document.getElementById("search-results").innerHTML = this.responseText;
        }
    };
    if (query.trim() == "") {
        document.getElementById("search-results").innerHTML = "";
        var newURL = "browse";
        window.history.replaceState({ path: newURL }, "", newURL);
        xhttp.open("POST", "browse-content", true);
        return xhttp.send();
    }
    xhttp.open("POST", "search-results?q=" + query, true);
    return xhttp.send();
}

function genre(query) {
    document.getElementById("genre-dropdown").value = query;
    document.getElementById("search-input").value = "";
    var newURL = "genre?q=" + encodeURIComponent(query);
    window.history.replaceState({ path: newURL }, "", newURL);
    var xhttp;
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("search-results").innerHTML = this.responseText;
        }
    };
    if (query == 0) {
        document.getElementById("search-results").innerHTML = "";
        var newURL = "browse";
        window.history.replaceState({ path: newURL }, "", newURL);
        xhttp.open("POST", "browse-content", true);
        return xhttp.send();
    }
    xhttp.open("POST", "genre-results?q=" + query, true);
    return xhttp.send();
}
