This module extends Func to have some direct methods for use by administrators running GlusterFS storage clusters.  This module is intended for us against the actual gluster nodes, not the client systems.

The initial release has support for the following:

  * gluster peer status
```
func "*" call gluster peer status
```
  * gluster volume info `[<volume name>]`
```
func "*" call gluster volume info [<volume name>]
```
  * gluster volume start `<volume name>`
```
func "*" call gluster volume start <volume name>
```
  * gluster volume start `<volume name>` force
```
func "*" call gluster volume forcestart <volume name>
```
  * gluster volume stop `<volume name>`
```
func "*" call gluster volume stop <volume name>
```
  * gluster volume stop --mode=script `<volume name>` force
```
func "*" call gluster volume forcestop <volume name>
```
  * cat /etc/glusterd/vols/`<volume name>`/cksum
```
func "*" call gluster volume cksum <volume name>
```
  * ps ax | grep `<volume name>`
```
func "*" call gluster volume process <volume name>
```