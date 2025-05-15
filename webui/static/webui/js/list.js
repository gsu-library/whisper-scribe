(() => {
   'use strict';


   // Enable tooltips
   const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
   const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl, {trigger : 'hover'}));


   // Initialize and configure DataTables
   let transcriptionsTable = new DataTable('#transcriptions', {
      order: [[2, 'asc']],
      columns: [
         { searchable: false, orderable: false },
         null,
         null,
         { searchable: false, orderable: false },
         { searchable: false, orderable: false },
         { searchable: false, orderable: false },
         { searchable: false, orderable: false },
         { searchable: false, orderable: false }
      ],
      columnDefs: [{
         targets: 2,
         render: DataTable.render.datetime('M/DD/YYYY h:mm a')
      }]
   });


   // Setup child rows
   transcriptionsTable.on('click', 'td.expand', event => {
      let tr = event.target.closest('tr');
      let row = transcriptionsTable.row(tr);

      if(row.child.isShown()) {
         row.child.hide();
      }
      else {
         row.child(tr.querySelector('.child').innerHTML).show();
      }
   });


   // Check before deleting transcription
   const deleteButtons = document.querySelectorAll('.delete-transcription');
   deleteButtons.forEach(button => {
      button.addEventListener('click', event => {
         const titleLink = event.target.closest('tr').querySelector('.title a');
         const confirmation = confirm('Are you sure you want to delete the transcription "' + titleLink.textContent + '"?');

         if(!confirmation) {
            event.stopPropagation();
            event.preventDefault();
         }
      });
   });
})();
