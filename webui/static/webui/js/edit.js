(() => {
   'use strict';
   const autoplay = document.querySelector('#autoplay');
   const mediaPlayer = document.querySelector('#media');
   const transcriptionId = window.location.pathname.split('/').pop();
   let transcriptionParts = document.querySelectorAll('.transcription-part');


   // Setup scroll to top button
   document.addEventListener('DOMContentLoaded', () => {
      const scrollButton = document.querySelector('#scrollToTop');
      const scrollYHeight = 300;

      // Initially show the button if scroll height is > scrollYHeight
      if(window.scrollY > scrollYHeight) {
         scrollButton.style.display = 'block';
      }

      window.addEventListener('scroll', () => {
         if(window.scrollY > scrollYHeight) {
            scrollButton.style.display = 'block';
         }
         else {
            scrollButton.style.display = 'none';
         }
      });

      scrollButton.addEventListener('click', e => {
         e.preventDefault();
         window.scrollTo({top: 0, behavior: 'smooth'});
      });
   });


   // Setup transcription part updates
   transcriptionParts.forEach(part => {
      part.addEventListener('change', async obj => {
         const data = {
            field: obj.target.dataset.field,
            value: obj.target.value
         };
         const result = await callApi('/api/transcriptions/' + transcriptionId, data, 'POST');

         if(result.status === 200) {
            part.classList.remove('error');
            part.classList.add('success');
         }
         else {
            part.classList.remove('success');
            part.classList.add('error');
         }
      });
   });


   // Setup all segment events
   let segments = document.querySelectorAll('.segment');
   segments.forEach(setupSegment);


   // Function: setupSegment
   // Adds events to segments
   function setupSegment(segment) {
      const segmentId = segment.dataset.index;
      let inputs = segment.querySelectorAll('input');
      let textareas =  segment.querySelectorAll('textarea');
      let buttons = segment.querySelectorAll('button');
      let startTime = document.querySelector('#start-' + segmentId);

      // Enable tooltips
      const tooltipTriggerList = segment.querySelectorAll('[data-bs-toggle="tooltip"]');
      const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl, {trigger : 'hover'}));

      // Update input fields on change
      inputs.forEach(input => {
         input.addEventListener('change', async obj => {
            const data = { field: obj.target.dataset.field }

            if(data.field === 'start' || data.field === 'end') {
               data['value'] = segmentTimeToSeconds(obj.target.value);
            }
            else {
               data['value'] = obj.target.value;
            }

            const result = await callApi('/api/segments/' + segmentId, data, 'POST');

            if(result.status === 200) {
               input.classList.remove('error');
               input.classList.add('success');
            }
            else {
               input.classList.remove('success');
               input.classList.add('error');
            }
         });
      });

      // Update textarea on change and add autoplay
      textareas.forEach(textarea => {
         // Autoplay
         textarea.addEventListener('focus', obj => {
            if(autoplay.checked) {
               let time = segmentTimeToSeconds(startTime.value);

               if(time) {
                  mediaPlayer.currentTime = time;
                  mediaPlayer.play();
               }
            }
         });

         // Update
         textarea.addEventListener('change', async obj => {
            const data = {
               field: obj.target.dataset.field,
               value: obj.target.value
            };
            const result = await callApi('/api/segments/' + segmentId, data, 'POST');

            if(result.status === 200) {
               textarea.classList.remove('error');
               textarea.classList.add('success');
            }
            else {
               textarea.classList.remove('success');
               textarea.classList.add('error');
            }
         });
      });

      // Add listeners to all buttons
      buttons.forEach(button => {
         const buttonType = button.dataset.type;

         button.addEventListener('click', () => {
            let time = segmentTimeToSeconds(startTime.value) ? startTime.value : 0;

            switch (buttonType) {
               case 'play':
                  mediaPlayer.currentTime = time;
                  mediaPlayer.play();
                  break;
               case 'pause':
                  mediaPlayer.pause();
                  break;
               case 'rewind':
                  let currentTime = mediaPlayer.currentTime;
                  let newTime = currentTime - 1.0;
                  mediaPlayer.currentTime = (newTime < 0) ? 0 : newTime;
                  break;
               case 'add-before':
                  createSegment(segmentId, -1);
                  break;
               case 'add-after':
                  createSegment(segmentId, 1);
                  break;
               case 'delete':
                  deleteSegment(segmentId);
                  break;
               default:
                  console.log('You should never see this.');
            }
         });
      });
   }


   // Function: createSegment
   async function createSegment(segmentId, where) {
      let otherSegment;
      let otherId = -1;
      const clickedSegment = document.querySelector(`.segment[data-index='${segmentId}']`);

      if(where < 0) {
         otherSegment = clickedSegment.previousElementSibling;
      }
      else if(where > 0) {
         otherSegment = clickedSegment.nextElementSibling;
      }
      else {
         console.log('Segment creation failed.');
         return;
      }

      if(otherSegment && otherSegment.classList.contains('segment')) {
         otherId = otherSegment.dataset.index;
      }

      const data = {
         segmentId: segmentId,
         otherId: otherId,
         where: where
      };

      const response = await callApi('/api/segments/', data, 'POST');

      if(response.status == 200) {
         const json = await response.json();
         let segment = newSegment(json.id, json.start, json.end);
         segment = segment.childNodes[0];
         // TODO: should not have to select child node here

         if(where < 0) { clickedSegment.before(segment);  }
         else if( where > 0) { clickedSegment.after(segment); }
         setupSegment(segment);
      }
      else {
         alert('Segment creation failed due to server error.')
      }
   }


   // Function: deleteSegment
   async function deleteSegment(segmentId) {
      let segment;

      // segmentId should never be 0 due to autoincrement - if it ever is this will not work on segment 0
      if(segmentId && (segment = document.querySelector(`.segment[data-index='${segmentId}']`))) {
         const data = { method: 'DELETE' };
         const response = await callApi('/api/segments/' + segmentId, data, 'POST');

         if(response.status == 204) {
            segment.remove();
         }
         else {
            alert('Segment deletion failed due to server error.')
         }
      }
   }


   // Function: callApi
   // Calls API to update a segment
   async function callApi(apiPath, data, method = 'GET') {
      let headers = {
         'Content-Type': 'application/json',
         'X-Requested-With': 'XMLHttpRequest',
      };

      if(method.toUpperCase() == 'POST') {
         headers['X-CSRFToken'] = document.querySelector('[name=csrfmiddlewaretoken]').value;
      }

      const response = await fetch(apiPath, {
         method: method.toUpperCase(),
         body: JSON.stringify(data),
         headers: headers,
         mode: 'same-origin',
      });

      // const responseData = await response.json();
      // return response.json();
      return response;
   }


   // Function newSegment
   // Creates and returns segment code
   function newSegment(segmentId, start, end) {
      // SEGMENT CHANGES MUST ALSO BE UPDATED IN EDIT.HTML!!!!
      let segmentCode = `<div class="segment mb-5" data-index="${segmentId}">
         <div class="row mb-3">
            <div class="col-3">
               <div class="form-floating">
                  <input type="text" class="form-control" id="speaker-${segmentId}" name="speaker-${segmentId}" value="" placeholder="" data-field="speaker" />
                  <label for="speaker-${segmentId}" >Speaker</label>
               </div>
            </div>

            <div class="col-2">
               <div class="form-floating">
                  <input type="text" class="form-control" id="start-${segmentId}" name="start-${segmentId}" value="${start}" placeholder="" data-field="start" />
                  <label for="start-${segmentId}">Start</label>
               </div>
            </div>

            <div class="col-2">
               <div class="form-floating">
                  <input type="text" class="form-control" id="end-${segmentId}" name="end-${segmentId}" value="${end}" placeholder="" data-field="end" />
                  <label for="end-${segmentId}">End</label>
               </div>
            </div>
         </div>

         <div class="row mb-3">
            <textarea class="form-control" id="text-${segmentId}" name="text-${segmentId}" data-field="text"></textarea>
         </div>

         <div>
            <div class="btn-group" role="group">
               <button type="button" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-title="Play" data-bs-placement="bottom" aria-label="Play" data-type="play"><i class="bi bi-play-fill"></i></button>
               <button type="button" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-title="Pause" data-bs-placement="bottom" aria-label="Pause" data-type="pause"><i class="bi bi-pause-fill"></i></button>
               <button type="button" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-title="Quick Rewind" data-bs-placement="bottom" aria-label="Quick Rewind" data-type="rewind"><i class="bi bi-arrow-counterclockwise"></i></button>
               <button type="button" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-title="Add Segment Before" data-bs-placement="bottom" aria-label="Add Segment Before" data-type="add-before"><i class="bi bi-arrow-bar-up"></i></button>
               <button type="button" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-title="Add Segment After" data-bs-placement="bottom" aria-label="Add Segment After" data-type="add-after"><i class="bi bi-arrow-bar-down"></i></button>
            </div>

            <div class="float-end" role="group">
               <button class="btn btn-outline-danger border-0 segment-delete" data-bs-title="Delete Segment" data-bs-placement="bottom" aria-label="Delete Segment" data-type="delete"><i class="bi bi-x-lg"></i></button>
            </div>
         </div>
      </div>`;

      let temp = document.createElement('div');
      temp.innerHTML = segmentCode;
      return temp;
   }


   // Function: segmentTimeToSeconds
   // Converts segment time format to seconds.
   function segmentTimeToSeconds(time) {
      const parts = time.split(':');
      let hours = 0;
      let minutes = 0;
      let seconds = 0;
      let milliseconds = 0;

      // Format is ss or ss.mill
      if(parts.length === 1) {
         const secondsParts = parts[0].split('.');
         seconds = parseInt(secondsParts[0], 10);

         if(secondsParts.length > 1) {
            milliseconds = parseInt(secondsParts[1], 10);
         }
      }
      // Format is mm:ss or mm:ss.mill
      else if(parts.length === 2) {
         minutes = parseInt(parts[0], 10);
         const secondsParts = parts[1].split('.');
         seconds = parseInt(secondsParts[0], 10);

         if(secondsParts.length > 1) {
            milliseconds = parseInt(secondsParts[1], 10);
         }
      }
      // Format is hh:mm:ss or hh:mm:ss.mill
      else if(parts.length === 3) {
         hours = parseInt(parts[0], 10);
         minutes = parseInt(parts[1], 10);
         const secondsParts = parts[2].split('.');
         seconds = parseInt(secondsParts[0], 10);

         if(secondsParts.length > 1) {
            milliseconds = parseInt(secondsParts[1], 10);
         }
      }

      const totalSeconds = (hours * 3600) + (minutes * 60) + seconds + (milliseconds / 1000);

      if(isNaN(totalSeconds)) {
         return null;
      }

      return totalSeconds;
   }
})();
