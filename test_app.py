import unittest
import pandas as pd
from hospitality_app.app import allocate_rooms, allocate_group, allocate_mixed_group

class TestRoomAllocation(unittest.TestCase):

    def setUp(self):
        # Prepare dummy data for testing
        self.groups_data = {
            'Group ID': [101, 102, 103, 104, 105],
            'Members': [3, 4, 2, 5, '5&3'],
            'Gender': ['Boys', 'Girls', 'Boys', 'Girls', '5 Boys & 3 Girls']
        }
        self.groups_df = pd.DataFrame(self.groups_data)

        self.hostels_data = {
            'Hostel Name': ['Boys Hostel A', 'Boys Hostel A', 'Girls Hostel B', 'Girls Hostel B'],
            'Room Number': [101, 102, 201, 202],
            'Capacity': [3, 4, 2, 5],
            'Gender': ['Boys', 'Boys', 'Girls', 'Girls']
        }
        self.hostels_df = pd.DataFrame(self.hostels_data)

    def test_allocate_group(self):
        # Testing allocation for boys
        boys_allocation = []
        allocated = allocate_group(boys_allocation, self.hostels_df[self.hostels_df['Gender'] == 'Boys'], 101, 3)
        self.assertTrue(allocated)
        self.assertEqual(len(boys_allocation), 1)
        self.assertEqual(boys_allocation[0]['Group ID'], 101)
        self.assertEqual(boys_allocation[0]['Members Allocated'], 3)

        # Testing allocation for girls
        girls_allocation = []
        allocated = allocate_group(girls_allocation, self.hostels_df[self.hostels_df['Gender'] == 'Girls'], 102, 2)
        self.assertTrue(allocated)
        self.assertEqual(len(girls_allocation), 1)
        self.assertEqual(girls_allocation[0]['Group ID'], 102)
        self.assertEqual(girls_allocation[0]['Members Allocated'], 2)

    def test_allocate_mixed_group(self):
        # Testing allocation for mixed group
        mixed_allocation = []
        boys_allocated = allocate_mixed_group(mixed_allocation, self.hostels_df[self.hostels_df['Gender'] == 'Boys'], 105, 5, 'Boys')
        girls_allocated = allocate_mixed_group(mixed_allocation, self.hostels_df[self.hostels_df['Gender'] == 'Girls'], 105, 3, 'Girls')
        self.assertEqual(boys_allocated, 5)
        self.assertEqual(girls_allocated, 3)
        self.assertEqual(len(mixed_allocation), 2)

    def test_allocate_rooms(self):
        # Test overall allocation
        group_csv_path = 'test_groups.csv'
        hostel_csv_path = 'test_hostels.csv'
        self.groups_df.to_csv(group_csv_path, index=False)
        self.hostels_df.to_csv(hostel_csv_path, index=False)

        output_path = allocate_rooms(group_csv_path, hostel_csv_path)
        output_df = pd.read_csv(output_path)

        # Check the allocation output
        self.assertIn('Group ID', output_df.columns)
        self.assertIn('Hostel Name', output_df.columns)
        self.assertIn('Room Number', output_df.columns)
        self.assertIn('Members Allocated', output_df.columns)

if __name__ == '__main__':
    unittest.main()
