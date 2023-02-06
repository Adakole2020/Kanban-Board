$(function() {
    $('#taskModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var taskCard = $(button).closest('.taskCard');
        var taskList = $(button).closest('.taskList');
        var task_id = taskCard.data("task-id");
        var task_name = taskCard.data("task-name");
        var task_content = taskCard.data("task-content");
        var task_state = taskList.data("task-state");
        var task_assignees = taskCard.data("task-assignees");
        $("#task-id").val(task_id);
        $("#task-name").val(task_name);
        $("#task-state").val(task_state);
        $("#task-content").text(task_content);
        $("#task-assignees").val(task_assignees);
    });
    $('#newTaskModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var taskList = $(button).closest('.taskList');
        var task_state = taskList.data("task-state");
        $("#new-task-state").val(task_state);
    });

    $('#editBoard').click(function(event) {
        if ($(this).hasClass("submitForm"))
            document.getElementById("board-form").requestSubmit();
        document.querySelectorAll(".boardEdit").forEach(function(element) {
            element.disabled = !element.disabled
        });
        $('#revert-div').toggleClass('d-none');
        $(this).parent().next().toggleClass("d-none");
        $('#addParticipantGroup').toggleClass("d-none");
        $(this).toggleClass("submitForm");
        $(this).toggleClass("btn-success btn-secondary");
        $(this).children('i').toggleClass("fa-check fa-pencil");
        if ($(this).prev().children('span').text() == "Edit Board")
            $(this).prev().children('span').text("Confirm Update Board");
        else
            $(this).prev().children('span').text("Edit Board");
    });


    $('#editTask').click(function(event) {
        if ($(this).hasClass("submitForm")) {
            $("#task-submit").click()
        }
        document.querySelectorAll("#taskEdit").forEach(function(element) {
            element.disabled = !element.disabled
        });
        $(this).parent().next().toggleClass("d-none");
        $(this).toggleClass("submitForm");
        $(this).toggleClass("btn-success btn-secondary");
        $(this).children('i').toggleClass("fa-check fa-pencil");
        if ($(this).prev().children('span').text() == "Edit Task")
            $(this).prev().children('span').text("Confirm Update Task")
        else
            $(this).prev().children('span').text("Edit Task");
    });

    $('#renewBoard').click(function(event) {
        $("#boardName").val();
        $("#boardDescription").text();
    })
});

const ID_RE = /(-)_(-)/;

/**
 * Replace the template index of an element (-_-) with the
 * given index.
 */
function replaceTemplateIndex(value, index) {
    return value.replace(ID_RE, '$1' + index + '$2');
}

/**
 * Adjust the indices of form fields when removing items.
 */
function adjustIndices(removedIndex) {
    var $forms = $('.participant-form');

    $forms.each(function(i) {
        var $form = $(this);
        var index = parseInt($form.data('index'));
        var newIndex = index - 1;

        if (index < removedIndex) {
            // Skip
            return true;
        }

        // This will replace the original index with the new one
        // only if it is found in the format -num-, preventing
        // accidental replacing of fields that may have numbers
        // intheir names.
        var regex = new RegExp('(-)' + index + '(-)');
        var repVal = '$1' + newIndex + '$2';

        // Change ID in form itself
        $form.attr('id', $form.attr('id').replace(index, newIndex));
        $form.data('index', newIndex);

        // Change IDs in form fields
        $form.find('label, input, select, textarea').each(function(j) {
            var $item = $(this);

            if ($item.is('label')) {
                // Update labels
                $item.attr('for', $item.attr('for').replace(regex, repVal));
                return;
            }

            // Update other fields
            $item.attr('id', $item.attr('id').replace(regex, repVal));
            $item.attr('name', $item.attr('name').replace(regex, repVal));
        });
    });
}

/**
 * Remove a form.
 */
function removeForm() {
    var $removedForm = $(this).closest('.participant-form');
    var removedIndex = parseInt($removedForm.data('index'));

    $removedForm.remove();

    // Update indices
    adjustIndices(removedIndex);
}

/**
 * Add a new form.
 */
function addForm() {
    var $templateForm = $('#participant-_-form');

    if ($templateForm.length === 0) {
        console.log('[ERROR] Cannot find template');
        return;
    }

    // Get Last index
    var $lastForm = $('.participant-form').last();

    var newIndex = 0;

    if ($lastForm.length > 0) {
        newIndex = parseInt($lastForm.data('index')) + 1;
    }

    // Add elements
    var $newForm = $templateForm.clone();

    console.log(newIndex, $lastForm);

    $newForm.attr('id', replaceTemplateIndex($newForm.attr('id'), newIndex));
    $newForm.data('index', newIndex);

    $newForm.find('label, input, select, textarea').each(function(idx) {
        var $item = $(this);

        if ($item.is('label')) {
            // Update labels
            $item.attr('for', replaceTemplateIndex($item.attr('for'), newIndex));
            return;
        }

        // Update other fields
        $item.attr('id', replaceTemplateIndex($item.attr('id'), newIndex));
        $item.attr('name', replaceTemplateIndex($item.attr('name'), newIndex));
    });

    // Append
    $('#participantGroup').append($newForm);
    $newForm.toggleClass('d-none participant-form');
    $newForm.find('.removeParticipant').click(removeForm);
}


$(document).ready(function() {
    $('#addParticipant').click(addForm);
    $('.removeParticipant').click(removeForm);
});