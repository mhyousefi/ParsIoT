class Commands:
    def __init__(self):
        self.user_controlling = False
        self.relay_values = [0, 0, 0, 0]
        self.smoke_led_status = 0
        self.water_level_led_status = 0

    def set_relay_values(self, new_values):
        self.relay_values = new_values

    def set_values(self, new_relay_values, smoke_led_new_value, water_level_led_new_value):
        self.smoke_led_status = smoke_led_new_value
        self.water_level_led_status = water_level_led_new_value
        if self.user_controlling is False:
            self.relay_values = new_relay_values

    def turn_man_override_off(self):
        self.user_controlling = False
        
    def turn_man_override_on(self):
		self.user_controlling = True

    def get_values(self):
        return [self.smoke_led_status, self.water_level_led_status] + self.relay_values
        
    def get_alarm_message(self):
		return str(self.smoke_led_status) + str(self.water_level_led_status)
