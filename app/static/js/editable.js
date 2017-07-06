$(document).ready(function() {
    //toggle `popup` / `inline` mode
    $.fn.editable.defaults.mode = 'inline';
    
    //Editable-x current fields in accordance with app.Models. but needs to correct the code improperly activating the editable feature.


$(document).ready(function() {
  $('#titles').editable();
  $('#tags').editable();
  $('#bodies').editable();
  $('#region').editable();
  $('#blocks').editable();
});

    //make status editable
    $('#status').editable({
        type: 'select',
        title: 'Select status',
        placement: 'right',
        value: 2,
        source: [
            {value: 1, text: 'status 1'},
            {value: 2, text: 'status 2'},
            {value: 3, text: 'status 3'}
        ]
        /*
        //uncomment these lines to send data on server
        ,pk: 1
        ,url: '/post'
        */
    });
});