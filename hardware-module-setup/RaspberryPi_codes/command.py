class Commands:
    def __init__(self):
        self.user_controlling = False
        self.relay_values = [0, 0, 0, 0]
        self.smoke_led_status = 0
        self.water_level_led_status = 0

    def apply_user_input(self, man_override_will_be_on, user_input):
        if man_override_will_be_on:
            self.user_controlling = True
            self.relay_values = user_input
        else:
            self.user_controlling = False

    def set_values(self, new_relay_values, smoke_led_new_status, water_level_led_new_status):
        self.smoke_led_status = smoke_led_new_status
        self.water_level_led_status = water_level_led_new_status
        if ~ self.user_controlling:
            self.relay_values = new_relay_values

    def get_values(self):
        return [self.smoke_led_status, self.water_level_led_status] + self.relay_values
