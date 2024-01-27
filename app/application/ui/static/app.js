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

function postVoteRequest(action, obj, unique_id, jwt) {
    fetch("/api/v1/discussion/vote", {
        method: "POST",
        headers: {
            'Authorization': 'Bearer ' + jwt,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            obj: obj,
            unique_id: unique_id,
            action: action,
        })
    })
}

function upvote(element, action, obj, unique_id, jwt) {
    let upVoteIcon = element.children[0];
    let upVoteClassList = upVoteIcon.classList;
    if (upVoteClassList.contains('bi-arrow-up-square')) {
        // mark upvote as active
        upVoteClassList.remove('bi-arrow-up-square')
        upVoteClassList.add('bi-arrow-up-square-fill')
        postVoteRequest('upvote', obj, unique_id, jwt);

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
        postVoteRequest('delete', obj, unique_id, jwt);
    }
}

function downvote(element, action, obj, unique_id, jwt) {
    let downVoteIcon = element.children[0];
    let downVoteClassList = downVoteIcon.classList;
    if (downVoteClassList.contains('bi-arrow-down-square')) {
        // mark downvote as active
        downVoteClassList.remove('bi-arrow-down-square')
        downVoteClassList.add('bi-arrow-down-square-fill')
        postVoteRequest('downvote', obj, unique_id, jwt);

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
        postVoteRequest('delete', obj, unique_id, jwt);
    }
}
