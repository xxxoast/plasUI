
var accept_task = $('#accept_task_btn')
var deny_task = $('#deny_task_btn')

function submit_table(to_be_submitted,tar_url){
	var data = to_be_submitted.bootstrapTable('getData');
	var json_data = JSON.stringify( data );
	console.log('submit data');
	for(i=0;i<data.length;i++)
		console.log(JSON.stringify( data[i] ));
  	$.ajax({
  		type:"POST",
        url: tar_url,
        data: { data : json_data },
        dataType: "json",
       	async: true,
        success: function (data, status) {
            if (status == "success") {
                console.log("Success");
            }
        },
        error: function () {
            console.log("error");
        },
        complete: function () {
        }
	});                        	
};	

accept_task.click(function () {
    var indexs = $.map(authorize_table.bootstrapTable('getSelections'), function (json_data) {
        return json_data.index;
    });
    console.log('remove exit row ' + indexs);
    authorize_table.bootstrapTable('remove', {
        field: 'index',
        values: indexs
    });
    submit_table(authorize_table,$SCRIPT_ROOT + '/auth/accept_task');
    authorize_table.bootstrapTable('refresh')
});


deny_task.click(function () {
    var indexs = $.map(authorize_table.bootstrapTable('getSelections'), function (json_data) {
        return json_data.index;
    });
    console.log('remove exit row ' + indexs);
    authorize_table.bootstrapTable('remove', {
        field: 'index',
        values: indexs
    });
    submit_table(authorize_table,$SCRIPT_ROOT + '/auth/deny_task');
    authorize_table.bootstrapTable('refresh')
});  