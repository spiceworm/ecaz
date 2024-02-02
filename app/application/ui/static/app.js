function deleteCommentOrThread(url, jwt) {
    fetch(url, {
        method: "DELETE",
        headers: {
            'Authorization': `Bearer ${jwt}`,
            'Content-Type': 'application/json',
        }
    }).then(resp => {
        // Reload the page so the original comment/thread text and poster are removed
        // TODO: find a less heavy handed way to do this.
        location.reload();
    })
}

function saveCommentOrThread(url, jwt) {
    fetch(url, {
        method: "POST",
        headers: {
            'Authorization': `Bearer ${jwt}`,
            'Content-Type': 'application/json',
        }
    }).then(resp => {
        // Reload the page so the 'Save' / 'Unsave' link changes
        // TODO: find a less heavy handed way to do this.
        location.reload();
    })
}

function unsaveCommentOrThread(url, jwt) {
    fetch(url, {
        method: "DELETE",
        headers: {
            'Authorization': `Bearer ${jwt}`,
            'Content-Type': 'application/json',
        }
    }).then(resp => {
        // Reload the page so the 'Save' / 'Unsave' link changes
        // TODO: find a less heavy handed way to do this.
        location.reload();
    })
}

function hideReplyForm(element) {
    element.closest('form').style.display = 'none';
}

function showReplyForm(element) {
    let replyForm = element.parentElement.parentElement.querySelector('#reply')
    replyForm.style.display = 'block';
}

function toggleCommentFolding(element) {
    const display = element.parentElement.parentElement.nextElementSibling.style.display;
    if (display === 'block') {
        // show child comments
        element.closest('a').text = '[+]';
        element.parentElement.parentElement.nextElementSibling.style.display = 'none';
    } else {
        // hide child comments
        element.closest('a').text  = '[-]';
        element.parentElement.parentElement.nextElementSibling.style.display = 'block';
    }
}

function postVoteRequest(action, url, jwt) {
    fetch(url, {
        method: "POST",
        headers: {
            'Authorization': `Bearer ${jwt}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            action: action,
        })
    })
}

function upvote(element, url, jwt) {
    let upVoteIcon = element.children[0];
    let upVoteClassList = upVoteIcon.classList;
    if (upVoteClassList.contains('bi-arrow-up-square')) {
        // mark upvote as active
        upVoteClassList.remove('bi-arrow-up-square')
        upVoteClassList.add('bi-arrow-up-square-fill')
        postVoteRequest('upvote', url, jwt);

        let downVoteIcon = element.nextElementSibling.children[0];
        let downVoteClassList = downVoteIcon.classList;
        if (downVoteClassList.contains('bi-arrow-down-square-fill')) {
            // mark downvote is inactive
            downVoteClassList.remove('bi-arrow-down-square-fill')
            downVoteClassList.add('bi-arrow-down-square')
        }
    } else if (upVoteClassList.contains('bi-arrow-up-square-fill')) {
        // mark upvote as inactive
        upVoteClassList.remove('bi-arrow-up-square-fill')
        upVoteClassList.add('bi-arrow-up-square')
        postVoteRequest('delete', url, jwt);
    }
}

function downvote(element, url, jwt) {
    let downVoteIcon = element.children[0];
    let downVoteClassList = downVoteIcon.classList;
    if (downVoteClassList.contains('bi-arrow-down-square')) {
        // mark downvote as active
        downVoteClassList.remove('bi-arrow-down-square')
        downVoteClassList.add('bi-arrow-down-square-fill')
        postVoteRequest('downvote', url, jwt);

        let upVoteIcon = element.previousElementSibling.children[0];
        let upVoteClassList = upVoteIcon.classList;
        if (upVoteClassList.contains('bi-arrow-up-square-fill')) {
            // mark upvote as inactive
            upVoteClassList.remove('bi-arrow-up-square-fill')
            upVoteClassList.add('bi-arrow-up-square')
        }
    } else if (downVoteClassList.contains('bi-arrow-down-square-fill')) {
        // mark downvote as inactive
        downVoteClassList.remove('bi-arrow-down-square-fill')
        downVoteClassList.add('bi-arrow-down-square')
        postVoteRequest('delete', url, jwt);
    }
}
