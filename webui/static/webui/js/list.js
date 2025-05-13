(() => {
   'use strict';


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
      ]
   });


   // Setup child rows
   const rowExpand = document.querySelectorAll('#transcriptions .expand');
   rowExpand.forEach(row => {
      row.addEventListener('click', event => {
         let tr = event.target.closest('tr');
         let dtRow = transcriptionsTable.row(tr);

         if(dtRow.child.isShown()) {
            dtRow.child.hide();
         }
         else {
            console.log(tr.querySelector('.child'));
            dtRow.child(tr.querySelector('.child').innerHTML).show();
         }
      });
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
