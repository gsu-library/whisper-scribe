(() => {
   'use strict';


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


   // Initialize and configure DataTables
   let transcriptionsTable = new DataTable('#transcriptions', {
      order: [[1, 'asc']],
      columns: [
         null,
         null,
         { searchable: false, orderable: false },
         { searchable: false, orderable: false },
         { searchable: false, orderable: false },
         { searchable: false, orderable: false },
         { searchable: false, orderable: false }
      ]
   });
})();
