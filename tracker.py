import time
from typing import Callable, Optional, Any, Tuple
import params
import simpleaudio as sa

class Tracker:
    def __init__(self) -> None:
        self._EAR_time_start : float = time.perf_counter()
        self._MAR_time_start : float = time.perf_counter()
        self._HPE_time_start : float = time.perf_counter()
        self._EAR_under_treshold_time : float = 0
        self._MAR_over_treshold_time : float = 0
        self._HPE_under_treshold_time : float = 0
        self._action_callback : Optional[Callable[[str, Any], Any]] = None
        self._wave_obj = sa.WaveObject.from_wave_file(params.ALARM_SOUND)
        self._play_obj : Optional[sa.PlayObject] = None
    
    def set_action_callback(self, callback : Callable[[str, Any], Any]) -> Callable[[str, Any], Any]:
        self._action_callback = callback
        return callback
    
    def update(self, ear : float, mar : float, hpe_x : float, cb_args: Tuple = () ) -> None:
        self._update_EAR(ear, cb_args)
        self._update_MAR(mar, cb_args)
        self._update_HPE(hpe_x, cb_args)
    
    def _update_EAR(self, ear : float, cb_args: Tuple) -> None:
        # if EAR is less than treshold
        if ear < params.EAR_TRESHOLD:
            # calculate time under treshold
            self._EAR_under_treshold_time += time.perf_counter() - self._EAR_time_start
            # if time under treshold is more than treshold
            if self._EAR_under_treshold_time > params.EAR_TIME_TRESHOLD:
                print("MEREM")
                # do action
                if self._action_callback:
                    self._action_callback("MEREM", *cb_args)
                self._EAR_under_treshold_time = 0
                if self._play_obj is None or not self._play_obj.is_playing():
                    self._play_obj = self._wave_obj.play()
        else:
            # reset time under treshold
            self._EAR_under_treshold_time = 0
            self._EAR_time_start = time.perf_counter()
    
    def _update_MAR(self, mar : float, cb_args: Tuple) -> None:
        # if MAR is more than treshold
        if mar > params.MAR_TRESHOLD:
            # calculate time over treshold
            self._MAR_over_treshold_time += time.perf_counter() - self._MAR_time_start
            # if time over treshold is more than treshold
            if self._MAR_over_treshold_time > params.MAR_TIME_TRESHOLD:
                print("MANGAP")
                # do action
                if self._action_callback:
                    self._action_callback("MANGAP", *cb_args)
                self._MAR_over_treshold_time = 0
                if self._play_obj is None or not self._play_obj.is_playing():
                    self._play_obj = self._wave_obj.play()
        else:
            # reset time over treshold
            self._MAR_over_treshold_time = 0
            self._MAR_time_start = time.perf_counter()
    
    def _update_HPE(self, hpe_x : float, cb_args: Tuple) -> None:
        # if head pose's x is less than treshold
        if hpe_x < params.X_LOWER:
            # calculate time under treshold
            self._HPE_under_treshold_time += time.perf_counter() - self._HPE_time_start
            # if time under treshold is more than treshold
            if self._HPE_under_treshold_time > params.HPE_TIME_TRESHOLD:
                print("NUNDUK")
                # do action
                if self._action_callback:
                    self._action_callback("NUNDUK", *cb_args)
                self._HPE_under_treshold_time = 0
                if self._play_obj is None or not self._play_obj.is_playing():
                    self._play_obj = self._wave_obj.play()
        else:
            # reset time under treshold
            self._HPE_under_treshold_time = 0
            self._HPE_time_start = time.perf_counter()


    

        
