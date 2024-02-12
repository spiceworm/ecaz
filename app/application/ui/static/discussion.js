function approveTopicSubscribeRequest(url, subscribe_request_id, jwt) {
    fetch(url, {
        method: "PUT",
        headers: {
            'Authorization': `Bearer ${jwt}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({subscribe_request_id: subscribe_request_id})
    }).then(resp => {
        // Reload the page so the original comment/thread text and poster are removed
        // TODO: find a less heavy handed way to do this.
        location.reload();
    })
}

function denyTopicSubscribeRequest(url, subscribe_request_id, jwt) {
    fetch(url, {
        method: "DELETE",
        headers: {
            'Authorization': `Bearer ${jwt}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({subscribe_request_id: subscribe_request_id})
    }).then(resp => {
        // Reload the page so the original comment/thread text and poster are removed
        // TODO: find a less heavy handed way to do this.
        location.reload();
    })
}

function deleteTopicBan(url, topic_ban_id, jwt) {
    fetch(url, {
        method: "DELETE",
        headers: {
            'Authorization': `Bearer ${jwt}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({topic_ban_id: topic_ban_id})
    }).then(resp => {
        // Reload the page so the original comment/thread text and poster are removed
        // TODO: find a less heavy handed way to do this.
        location.reload();
    })
}

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

function hideEditFields(comment_id) {
    let commentText = document.getElementById(`body-${comment_id}`)
    commentText.hidden = false;

    let editDiv = document.getElementById(`edit-${comment_id}`);
    editDiv.hidden = true;
}

function saveEditComment(comment_id, url, jwt) {
    const editInput = document.getElementById(`editInput-${comment_id}`);

    fetch(url, {
        method: "POST",
        headers: {
            'Authorization': `Bearer ${jwt}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({body: editInput.value})
    }).then(resp => {
        let commentText = document.getElementById(`body-${comment_id}`)
        commentText.innerText = editInput.value;
        hideEditFields(comment_id);
    })
}

function saveEditThread(comment_id, url, jwt) {
    const editInput = document.getElementById(`editInput-${comment_id}`);

    fetch(url, {
        method: "POST",
        headers: {
            'Authorization': `Bearer ${jwt}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({body: editInput.value})
    }).then(resp => {
        let commentText = document.getElementById(`body-${comment_id}`);

        // Convert markdown in edit field back to HTML before saving it
        const converter = new showdown.Converter();
        commentText.innerHTML = converter.makeHtml(editInput.value);

        hideEditFields(comment_id);
    })
}

function showEditCommentFields(comment_id) {
    let commentText = document.getElementById(`body-${comment_id}`)
    commentText.hidden = true;

    let editInput = document.getElementById(`editInput-${comment_id}`);
    editInput.value = commentText.textContent;

    let editDiv = document.getElementById(`edit-${comment_id}`);
    editDiv.hidden = false;
}

function showEditThreadFields(comment_id) {
    let commentText = document.getElementById(`body-${comment_id}`)
    commentText.hidden = true;

    let editInput = document.getElementById(`editInput-${comment_id}`);

    // Convert HTML thread body to markdown so the user can edit markdown
    const turndownService = new TurndownService();
    editInput.value = turndownService.turndown(commentText.innerHTML);

    let editDiv = document.getElementById(`edit-${comment_id}`);
    editDiv.hidden = false;
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

function subscribe(url, jwt) {
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

function unsubscribe(url, jwt) {
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

function toggleExpiresAtNumber() {
    const expires_dropdown = document.getElementById("expires_at_unit");
    let expires_input = document.getElementById("expires_at_number");
    expires_input.disabled = (expires_dropdown.value === "Never");
}

function postTopicSubscribeRequest(url, jwt) {
    fetch(url, {
        method: "POST",
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
