q = [('htttp:s3url', 'baf78331-a643-4097-ae05-bec243be6b2a', None), ('htttp:s3url1', 'eea63fee-ab08-4996-99cc-3be9ff6ae6ad', None), ('htttp:s3url2', '867b287a-c40b-4e46-a568-e8ff0b46ad5b', None), ('htttp:feklrjgzoier', '3526798d-e3ea-446e-8744-f375ba361109', None)]
s3presigned_url = s3_manager.generate_presigned_url(q[0][1], q[0][2])
for element in q:
    print(element[0])
