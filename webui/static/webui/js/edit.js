(() => {
   'use strict';
   const autoplay = document.querySelector('#autoplay');
   const mediaPlayer = document.querySelector('#media');
   const transcriptionId = window.location.pathname.split('/').pop();
   let transcriptionParts = document.querySelectorAll('.transcription-part');


   // On DOM load
   document.addEventListener('DOMContentLoaded', () => {
      // Setup scroll to top button
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

      scrollButton.addEventListener('click', event => {
         event.preventDefault();
         window.scrollTo({top: 0, behavior: 'smooth'});
      });
   });


   // Setup transcription part updates
   transcriptionParts.forEach(part => {
      part.addEventListener('change', async event => {
         const data = {
            field: event.target.dataset.field,
            value: event.target.value
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
         input.addEventListener('change', async event => {
            const data = { field: event.target.dataset.field }

            if(data.field === 'start' || data.field === 'end') {
               data['value'] = segmentTimeToSeconds(event.target.value);
            }
            else {
               data['value'] = event.target.value;
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
         textarea.addEventListener('focus', () => {
            if(autoplay.checked) {
               let time = segmentTimeToSeconds(startTime.value);

               if(time) {
                  mediaPlayer.currentTime = time;
                  mediaPlayer.play();
               }
            }
         });

         textarea.addEventListener('change', async event => {
            const data = {
               field: event.target.dataset.field,
               value: event.target.value
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
            switch (buttonType) {
               case 'play':
                  mediaPlayer.currentTime = segmentTimeToSeconds(startTime.value, false);
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
         alert('Segment creation failed due to placement issue.');
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
         let wrapper = document.createElement('div');
         wrapper.innerHTML = json.segment.trim();
         let segment = wrapper.childNodes[0];

         if(where < 0) { clickedSegment.before(segment);  }
         else if( where > 0) { clickedSegment.after(segment); }
         setupSegment(segment);
      }
      else {
         alert('Segment creation failed due to server error.');
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
            let button = segment.querySelector('.segment-delete');
            let tooltip = bootstrap.Tooltip.getInstance(button);

            if(tooltip) {
               tooltip.dispose();
            }

            segment.remove();
         }
         else {
            alert('Segment deletion failed due to server error.');
         }
      }

      // If there are no more segments reload the page to show the add segment code
      const segments = document.querySelectorAll('.segment');

      if(segments.length === 0) {
         window.location.reload();
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


   // Function: segmentTimeToSeconds
   // Converts segment time format to seconds.
   function segmentTimeToSeconds(time, returnNull = true) {
      const parts = time.split(':');
      let hours = 0;
      let minutes = 0;
      let seconds = 0;
      let milliseconds = 0;

      // Helper function to parse seconds and milliseconds
      const parseSecondsAndMills = (secondsAndMills) => {
         let samParts = secondsAndMills.split('.');
         if(samParts[0] === '') { samParts[0] = '0'; }
         let seconds = parseInt(samParts[0], 10);
         let milliseconds = 0;

         if(samParts.length > 1) {
            let msString = samParts[1];

            if (msString.length === 1) {
                milliseconds = parseInt(msString + '00', 10);
            } else if (msString.length === 2) {
                milliseconds = parseInt(msString + '0', 10);
            } else {
                milliseconds = parseInt(msString.substring(0, 3), 10);
            }
         }

         return { seconds: seconds, milliseconds: milliseconds };
      };

      // Format is ss or ss.mill
      if(parts.length === 1) {
         const { seconds: s, milliseconds: ms } = parseSecondsAndMills(parts[0]);
         seconds = s;
         milliseconds = ms;
      }
      // Format is mm:ss or mm:ss.mill
      else if(parts.length === 2) {
         minutes = parseInt(parts[0], 10);
         const { seconds: s, milliseconds: ms } = parseSecondsAndMills(parts[1]);
         seconds = s;
         milliseconds = ms;
      }
      // Format is hh:mm:ss or hh:mm:ss.mill
      else if(parts.length === 3) {
         hours = parseInt(parts[0], 10);
         minutes = parseInt(parts[1], 10);
         const { seconds: s, milliseconds: ms } = parseSecondsAndMills(parts[2]);
         seconds = s;
         milliseconds = ms;
      }

      const totalSeconds = (hours * 3600) + (minutes * 60) + seconds + (milliseconds / 1000);

      if(isNaN(totalSeconds)) {
         return returnNull ? null : 0;
      }

      return totalSeconds;
   }
})();
